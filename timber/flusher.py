# coding: utf-8
from __future__ import print_function, unicode_literals
import sys
import time
import threading

from .compat import queue

RETRY_SCHEDULE = (1, 10, 60)  # seconds


class FlushWorker(threading.Thread):
    def __init__(self, upload, pipe, buffer_capacity, flush_interval):
        threading.Thread.__init__(self)
        self.parent_thread = threading.currentThread()
        self.upload = upload
        self.pipe = pipe
        self.buffer_capacity = buffer_capacity
        self.flush_interval = flush_interval

    def run(self):
        while True:
            self.step()

    def step(self):
        last_flush = time.time()
        timeout = _initial_timeout(self.flush_interval)
        frame = []
        # If the parent thread has exited but there are still outstanding
        # events, attempt to send them before exiting.
        shutdown = not self.parent_thread.is_alive()

        # Fill phase: take events out of the queue and group them for sending.
        # Takes up to `buffer_capacity` events out of the queue and groups them
        # for sending; may send fewer than `buffer_capacity` events if
        # `flush_interval` seconds have passed without sending any events.
        while len(frame) < self.buffer_capacity and timeout > 0:
            try:
                # When not in the shutdown phase, this will block for up to
                # `timeout` seconds waiting for a new entry to be placed in
                # `pipe`. On each loop `timeout` is set to be the remaining
                # time in the flush period, so that exactly as soon as the
                # timeout period is over any entries in `frame` will be
                # sent.
                entry = self.pipe.get(block=(not shutdown), timeout=timeout)
                frame.append(entry)
                self.pipe.task_done()
            except queue.Empty:
                # queue.Empty is raised if the timeout expires before a new
                # entry is placed into the queue, or if a nonblocking `.get`
                # finds nothing in the queue. In the former case, the flush
                # interval has expired and the worker should flush any
                # outstanding events. In the latter case, there are no more
                # events to be sent and the worker should flush any outstanding
                # events. In both cases, we break this loop and continue to the
                # send phase.
                break
            timeout = _calculate_timeout(last_flush, self.flush_interval)

        # Send phase: takes the outstanding events (up to `buffer_capacity`
        # count) and sends them to the Timber endpoint all at once. If the
        # request fails in a way that can be retried, it is retried with an
        # exponential backoff in between attempts.
        if frame:
            for delay in RETRY_SCHEDULE + (None, ):
                response = self.upload(frame)
                if not _should_retry(response.status_code):
                    break
                if delay is not None:
                    time.sleep(delay)

        if shutdown:
            sys.exit(0)


def _initial_timeout(flush_interval):
    return flush_interval


def _calculate_timeout(last_flush, flush_interval):
    elapsed = time.time() - last_flush
    timeout = max(flush_interval - elapsed, 0)
    return timeout


def _should_retry(status_code):
    return 500 <= status_code < 600
