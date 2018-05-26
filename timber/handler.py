# coding: utf-8
from __future__ import print_function, unicode_literals
import logging

from .compat import queue
from .constants import Default
from .flusher import FlushWorker
from .uploader import Uploader
from .log_entry import create_log_entry


class TimberHandler(logging.Handler):
    def __init__(self, api_key, endpoint=Default.endpoint,
                 buffer_capacity=Default.buffer_capacity,
                 flush_interval=Default.flush_interval,
                 raise_exceptions=Default.raise_exceptions,
                 drop_extra_events=Default.drop_extra_events,
                 context=Default.context,
                 level=logging.NOTSET):
        super(TimberHandler, self).__init__(level=level)
        self.api_key = api_key
        self.endpoint = endpoint
        self.context = context
        self.queue = queue.Queue(maxsize=buffer_capacity)
        self.uploader = Uploader(self.api_key, self.endpoint)
        self.drop_extra_events = drop_extra_events
        self.buffer_capacity = buffer_capacity
        self.flush_interval = flush_interval
        self.raise_exceptions = raise_exceptions
        self.dropcount = 0
        self.flush_thread = FlushWorker(
            self.uploader,
            self.queue,
            self.buffer_capacity,
            self.flush_interval
        )
        self.flush_thread.start()

    def emit(self, record):
        try:
            if not self.flush_thread.is_alive():
                self.start_flush_thread()
            log_entry = create_log_entry(self, record)
            try:
                self.queue.put(log_entry, block=(not self.drop_extra_events))
            except queue.Full:
                # Only raised when not blocking, which means that extra events
                # should be dropped.
                self.dropcount += 1
                pass
        except Exception as e:
            if self.raise_exceptions:
                raise e
