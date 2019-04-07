# coding: utf-8
from __future__ import print_function, unicode_literals
import logging
import multiprocessing

from .compat import queue
from .helpers import DEFAULT_CONTEXT
from .flusher import FlushWorker
from .uploader import Uploader
from .frame import create_frame

DEFAULT_HOST = 'https://logs.timber.io'
DEFAULT_BUFFER_CAPACITY = 1000
DEFAULT_FLUSH_INTERVAL = 2
DEFAULT_RAISE_EXCEPTIONS = False
DEFAULT_DROP_EXTRA_EVENTS = True


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
        self.pipe = multiprocessing.JoinableQueue(maxsize=buffer_capacity)
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
        if self._is_main_process():
            self.flush_thread.start()

    def _is_main_process(self):
        return multiprocessing.current_process()._parent_pid == None

    def emit(self, record):
        try:
            if self._is_main_process() and not self.flush_thread.is_alive():
                self.flush_thread.start()
            message = self.format(record)
            frame = create_frame(record, message, self.context)
            try:
                self.pipe.put(frame, block=(not self.drop_extra_events))
            except queue.Full:
                # Only raised when not blocking, which means that extra events
                # should be dropped.
                self.dropcount += 1
                pass
        except Exception as e:
            if self.raise_exceptions:
                raise e
