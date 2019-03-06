# coding: utf-8
from __future__ import print_function, unicode_literals
import logging

from .compat import queue
from .helpers import TimberContext
from .flusher import FlushWorker
from .uploader import Uploader
from .log_entry import create_log_entry

DEFAULT_HOST = 'https://logs.timber.io'
DEFAULT_BUFFER_CAPACITY = 1000
DEFAULT_FLUSH_INTERVAL = 2
DEFAULT_RAISE_EXCEPTIONS = False
DEFAULT_DROP_EXTRA_EVENTS = True
DEFAULT_CONTEXT = TimberContext()


class TimberHandler(logging.Handler):
    def __init__(self,
                 api_key,
                 source_id,
                 host=DEFAULT_HOST,
                 buffer_capacity=DEFAULT_BUFFER_CAPACITY,
                 flush_interval=DEFAULT_FLUSH_INTERVAL,
                 raise_exceptions=DEFAULT_RAISE_EXCEPTIONS,
                 drop_extra_events=DEFAULT_DROP_EXTRA_EVENTS,
                 context=DEFAULT_CONTEXT,
                 level=logging.NOTSET):
        super(TimberHandler, self).__init__(level=level)
        self.api_key = api_key
        self.source_id = source_id
        self.host = host
        self.context = context
        self.pipe = queue.Queue(maxsize=buffer_capacity)
        self.uploader = Uploader(self.api_key, self.source_id, self.host)
        self.drop_extra_events = drop_extra_events
        self.buffer_capacity = buffer_capacity
        self.flush_interval = flush_interval
        self.raise_exceptions = raise_exceptions
        self.dropcount = 0
        self.flush_thread = FlushWorker(
            self.uploader,
            self.pipe,
            self.buffer_capacity,
            self.flush_interval
        )
        self.flush_thread.start()

    def emit(self, record):
        try:
            if not self.flush_thread.is_alive():
                self.flush_thread.start()
            log_entry = create_log_entry(self, record)
            try:
                self.pipe.put(log_entry, block=(not self.drop_extra_events))
            except queue.Full:
                # Only raised when not blocking, which means that extra events
                # should be dropped.
                self.dropcount += 1
                pass
        except Exception as e:
            if self.raise_exceptions:
                raise e
