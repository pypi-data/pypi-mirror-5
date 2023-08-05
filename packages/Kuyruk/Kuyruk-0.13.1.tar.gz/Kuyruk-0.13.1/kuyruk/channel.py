import errno
import select
import logging

import pika

logger = logging.getLogger(__name__)


class LazyChannel(object):

    def __init__(self, host='localhost', port=5672, virtual_host='/',
                 user='guest', password='guest'):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.user = user
        self.password = password
        self.connection = None
        self.channel = None

    @classmethod
    def from_config(cls, config):
        return cls(
            config.RABBIT_HOST, config.RABBIT_PORT, config.RABBIT_VIRTUAL_HOST,
            config.RABBIT_USER, config.RABBIT_PASSWORD)

    def __getattr__(self, item):
        """Open the channel on first access."""
        if not self.is_open:
            self.open()
        return getattr(self.channel, item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def is_open(self):
        if self.channel is None:
            return False
        return self.channel.is_open

    def open(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat_interval=600,
            socket_timeout=2,
            connection_attempts=2)
        self.connection = pika.BlockingConnection(parameters)
        logger.info('Connected to RabbitMQ')
        self.channel = self.connection.channel()
        logger.debug('Opened channel')

    def close(self):
        if self.is_open:
            self.channel.close()
            self.connection.close()
            logger.info('%r closed', self)

    def tx_commit(self):
        # When a signal is received while tx_commit() is running
        # select.poll() throws an exception, complaining that syscall has
        # interrupted. This while loop ensures that the trx is commited
        # without raising an error.
        while True:
            try:
                self.channel.tx_commit()
                break
            except select.error as e:
                if e.args[0] != errno.EINTR:
                    raise
