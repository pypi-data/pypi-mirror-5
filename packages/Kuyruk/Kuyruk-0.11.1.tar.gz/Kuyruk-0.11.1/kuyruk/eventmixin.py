from __future__ import absolute_import
import logging
from kuyruk import signals
from functools import wraps

logger = logging.getLogger(__name__)


class EventMixin(object):
    """This mixin class contains some decorator methods for wrapping handler
    functions to run on certain signals.

    """
    def before_task(self, f):
        self.connect_signal(signals.before_task, f)
        return f

    def after_task(self, f):
        self.connect_signal(signals.after_task, f)
        return f

    def on_return(self, f):
        self.connect_signal(signals.on_return, f)
        return f

    def on_exception(self, f):
        self.connect_signal(signals.on_exception, f)
        return f

    def connect_signal(self, signal, handler):
        signal.connect(insert_sender(handler), sender=self, weak=False)


def insert_sender(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return f(*args[1:], **kwargs)
    return inner
