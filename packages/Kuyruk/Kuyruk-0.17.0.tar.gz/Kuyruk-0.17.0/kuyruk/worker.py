from __future__ import absolute_import
import os
import sys
import socket
import signal
import logging
import traceback
import multiprocessing
from time import time, sleep
from datetime import datetime
from functools import wraps
from setproctitle import setproctitle
import kuyruk
from kuyruk import importer
from kuyruk.queue import Queue
from kuyruk.process import KuyrukProcess
from kuyruk.helpers import start_daemon_thread
from kuyruk.consumer import Consumer
from kuyruk.exceptions import Reject, ObjectNotFound, Timeout, InvalidTask
from kuyruk.helpers.json_datetime import JSONEncoder

try:
    import raven
except ImportError:
    raven = None

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)


def set_current_task(f):
    """Save current task and it's arguments in self so we can send them to
    manager as stats."""
    @wraps(f)
    def inner(self, task, args, kwargs):
        self.current_task = task
        self.current_args = args
        self.current_kwargs = kwargs
        try:
            return f(self, task, args, kwargs)
        finally:
            self.current_task = None
            self.current_args = None
            self.current_kwargs = None
    return inner


class Worker(KuyrukProcess):
    """Consumes messages from a queue and runs tasks.

    :param queue_name: The queue name to work on
    :param config: A :class:`~kuyurk.config.Config` object

    """
    def __init__(self, kuyruk, queue_name):
        super(Worker, self).__init__(kuyruk)
        self.channel = self.kuyruk._channel()
        is_local = queue_name.startswith('@')
        queue_name = queue_name.lstrip('@')
        self.queue = Queue(queue_name, self.channel, local=is_local)
        self.consumer = Consumer(self.queue)
        self.current_task = None
        self.current_args = None
        self.current_kwargs = None
        self.daemon_threads = [
            self.watch_master,
            self.watch_load,
            self.shutdown_timer,
        ]
        if self.config.MAX_LOAD is None:
            self.config.MAX_LOAD = multiprocessing.cpu_count()

        if self.config.SENTRY_DSN:
            if raven is None:
                raise ImportError('Cannot import raven. Please install it with '
                                  '"pip install raven".')
            self.sentry = raven.Client(self.config.SENTRY_DSN)
        else:
            self.sentry = None

        if self.config.SAVE_FAILED_TASKS:
            if redis is None:
                raise ImportError('Cannot import redis. Please install it with '
                                  '"pip install redis".')
            self.redis = redis.StrictRedis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD)
        else:
            self.redis = None

    def run(self):
        """Runs the worker and opens a connection to RabbitMQ.
        After connection is opened, starts consuming messages.
        Consuming is cancelled if an external signal is received.

        """
        super(Worker, self).run()
        setproctitle("kuyruk: worker on %s" % self.queue.name)
        self.queue.declare()
        self.queue.basic_qos(prefetch_count=1)
        self.queue.tx_select()
        self.import_modules()
        self.start_daemon_threads()
        self.maybe_start_manager_thread()
        self.consume_messages()
        logger.debug("End run worker")

    def consume_messages(self):
        """Consumes messages from the queue and run tasks until
        consumer is cancelled via a signal or another thread.

        """
        with self.consumer.consume() as messages:
            for message in messages:
                self.process_message(message)
                self.queue.tx_commit()
                logger.debug("Committed transaction")

    def start_daemon_threads(self):
        """Start the function as threads listed in self.daemon_thread."""
        for f in self.daemon_threads:
            start_daemon_thread(f)

    def import_modules(self):
        """Import modules defined in the configuration.
        This method is called before start consuming messages.

        """
        for module in self.config.IMPORTS:
            importer.import_module(module, self.config.IMPORT_PATH)

    def process_message(self, message):
        """Processes the message received from the queue."""
        try:
            task_description = message.get_object()
            logger.info("Processing task: %r", task_description)
        except Exception:
            message.ack()
            logger.error("Canot decode message. Dropped!")
            return

        task = None
        try:
            task = self.import_task(task_description)
            args, kwargs = task_description['args'], task_description['kwargs']
            self.apply_task(task, args, kwargs)
        except Reject:
            logger.warning('Task is rejected')
            sleep(1)  # Prevent cpu burning
            message.reject()
        except ObjectNotFound:
            self.handle_not_found(message, task_description, task)
        except Timeout:
            self.handle_timeout(message, task_description, task)
        except InvalidTask:
            self.handle_invalid(message, task_description, task)
        except Exception:
            self.handle_exception(message, task_description, task)
        else:
            logger.info('Task is successful')
            message.ack()
        finally:
            logger.debug("Processing task is finished")

    def handle_exception(self, message, task_description, task):
        """Handles the exception while processing the message."""
        logger.error('Task raised an exception')
        logger.error(traceback.format_exc())
        retry_count = task_description.get('retry', 0)
        if retry_count:
            logger.debug('Retry count: %s', retry_count)
            message.discard()
            task_description['retry'] = retry_count - 1
            self.queue.send(task_description)
        else:
            logger.debug('No retry left')
            self.capture_exception(task_description)
            message.discard()
            if self.config.SAVE_FAILED_TASKS:
                self.save_failed_task(task_description, task)

    def handle_not_found(self, message, task_description, task):
        """Called if the task is class task but the object with the given id
        is not found. The default action is logging the error and acking
        the message.

        """
        logger.error(
            "<%s.%s id=%r> is not found",
            task_description['module'],
            task_description['class'],
            task_description['args'][0])
        message.ack()

    def handle_timeout(self, message, task_description, task):
        """Called when the task is timed out while running the wrapped
        function.

        """
        logger.error('Task has timed out.')
        self.handle_exception(message, task_description, task)

    def handle_invalid(self, message, task_description, task):
        """Called when the message from queue is invalid."""
        logger.error("Invalid message.")
        self.capture_exception(task_description)
        message.discard()

    def save_failed_task(self, task_description, task):
        """Saves the task to ``kuyruk_failed`` queue. Failed tasks can be
        investigated later and requeued with ``kuyruk reuqueue`` command.

        """
        logger.info('Saving failed task')
        task_description['queue'] = self.queue.name
        task_description['worker_hostname'] = socket.gethostname()
        task_description['worker_pid'] = os.getpid()
        task_description['worker_cmd'] = ' '.join(sys.argv)
        task_description['worker_timestamp'] = datetime.utcnow()
        task_description['exception'] = traceback.format_exc()
        exc_type = sys.exc_info()[0]
        task_description['exception_type'] = "%s.%s" % (
            exc_type.__module__, exc_type.__name__)

        try:
            # Convert object to id for class tasks
            if task_description['class'] or task.arg_class:
                args = task_description['args']
                args[0] = args[0].id
                task_description['args'] = args

            self.redis.hset('failed_tasks', task_description['id'],
                            JSONEncoder().encode(task_description))
            logger.debug('Saved')
        except Exception:
            logger.error('Cannot save failed task to Redis!')
            logger.debug(traceback.format_exc())
            if self.sentry:
                self.sentry.captureException()

    @set_current_task
    def apply_task(self, task, args, kwargs):
        """Imports and runs the wrapped function in task."""

        # Fetch the object if class task
        cls = task.arg_class or task.cls
        if cls:
            if not args:
                raise InvalidTask

            obj_id = args[0]
            if not isinstance(obj_id, cls):
                obj = cls.get(obj_id)
                if obj is None:
                    raise ObjectNotFound

                args[0] = obj

        result = task.apply(*args, **kwargs)
        logger.debug('Result: %r', result)

    def import_task(self, task_description):
        """This is the method where user modules are loaded."""
        module, function, cls = (
            task_description['module'],
            task_description['function'],
            task_description['class'])
        return importer.import_task(
            module, cls, function, self.config.IMPORT_PATH)

    def capture_exception(self, task_description):
        """Sends the exceptin in current stack to Sentry."""
        if self.sentry:
            ident = self.sentry.get_ident(self.sentry.captureException(
                extra={
                    'task_description': task_description,
                    'hostname': socket.gethostname(),
                    'pid': os.getpid(),
                    'uptime': self.uptime}))
            logger.error("Exception caught; reference is %s", ident)
            task_description['sentry_id'] = ident

    def is_master_alive(self):
        ppid = os.getppid()
        if ppid == 1:
            return False

        try:
            os.kill(ppid, 0)
            return True
        except OSError:
            return False

    def watch_master(self):
        """Watch the master and shutdown gracefully when it is dead."""
        while True:
            if not self.is_master_alive():
                logger.critical('Master is dead')
                self.warm_shutdown()
            sleep(1)

    def watch_load(self):
        """Pause consuming messages if lood goes above the allowed limit."""
        while not self.shutdown_pending.is_set():
            load = os.getloadavg()[0]
            if load > self.config.MAX_LOAD:
                logger.warning('Load is high (%s), pausing consume', load)
                self.consumer.pause(10)
            sleep(1)

    def shutdown_timer(self):
        """Counts down from MAX_WORKER_RUN_TIME. When it reaches zero sutdown
        gracefully.

        """
        if not self.config.MAX_WORKER_RUN_TIME:
            return

        while True:
            sleep(1)
            passed = time() - self.started
            if passed > self.config.MAX_WORKER_RUN_TIME:
                logger.warning('Run time reached zero')
                self.warm_shutdown()

    def register_signals(self):
        super(Worker, self).register_signals()
        signal.signal(signal.SIGTERM, self.handle_sigterm)

    def handle_sigterm(self, signum, frame):
        """Initiates a warm shutdown."""
        logger.warning("Catched SIGTERM")
        self.warm_shutdown()

    def warm_shutdown(self, sigint=False):
        """Shutdown gracefully."""
        super(Worker, self).warm_shutdown(sigint)
        self.consumer.stop()

    def get_stats(self):
        """Generate stats to be sent to manager."""
        method = self.queue.declare().method
        try:
            current_task = self.current_task.name
        except AttributeError:
            current_task = None

        return {
            'type': 'worker',
            'hostname': socket.gethostname(),
            'uptime': self.uptime,
            'pid': os.getpid(),
            'ppid': os.getppid(),
            'version': kuyruk.__version__,
            'current_task': current_task,
            'current_args': self.current_args,
            'current_kwargs': self.current_kwargs,
            'consuming': self.consumer.consuming,
            'queue': {
                'name': method.queue,
                'messages_ready': method.message_count,
                'consumers': method.consumer_count,
            }
        }
