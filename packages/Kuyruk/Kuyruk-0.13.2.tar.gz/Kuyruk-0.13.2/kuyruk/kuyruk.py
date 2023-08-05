from __future__ import absolute_import
import logging
import kuyruk.exceptions
from kuyruk.task import Task
from kuyruk.config import Config
from kuyruk.events import EventMixin

logger = logging.getLogger(__name__)


class Kuyruk(EventMixin):
    """
    Main class for Kuyruk distributed task queue. It holds the configuration
    values and provides a task decorator for user application

    :param config: A module that contains configuration options.
                   See :ref:`configuration-options` for default values.

    """
    Reject = kuyruk.exceptions.Reject  # Shortcut for raising from tasks

    def __init__(self, config=None, task_class=Task):
        self.task_class = task_class
        self.config = Config()
        if config:
            self.config.from_object(config)

    def task(self, queue='kuyruk', eager=False, retry=0, task_class=None,
             max_run_time=None):
        """Wrap functions with this decorator to convert them to background
        tasks. After wrapping, calling the function will send a message to
        queue instead of running the function.

        :param queue: Queue name for the tasks.
        :param eager: Run task in process, do not use RabbitMQ.
        :param retry: Retry this times before give up.
        :param task_class: Custom task class.
            Must be a subclass of :class:`~Task`.
            If this is :const:`None` then :attr:`Task.task_class` will be used.
        :param max_run_time: Maximum allowed time in seconds for task to
            complete.
        :return: Callable :class:`~Task` object wrapping the original function.

        """
        def decorator():
            def inner(f):
                # Function may be wrapped with no-arg decorator
                queue_ = 'kuyruk' if callable(queue) else queue

                task_class_ = task_class or self.task_class
                return task_class_(
                    f, self,
                    queue=queue_, eager=eager,
                    retry=retry, max_run_time=max_run_time)
            return inner

        if callable(queue):
            logger.debug('task without args')
            return decorator()(queue)
        else:
            logger.debug('task with args')
            return decorator()
