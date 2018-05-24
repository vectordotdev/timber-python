# coding: utf-8
from __future__ import print_function, unicode_literals
import base64
import json
import logging
import queue
import requests
import sys
import time
import threading
from datetime import datetime

from timber.constants import Default, RETRY_SCHEDULE
from timber.helpers import make_context
from timber.schema import validate

context = Default.context


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
        self.uploader = _make_uploader(self.endpoint, self.api_key)
        self.drop_extra_events = drop_extra_events
        self.buffer_capacity = buffer_capacity
        self.flush_interval = flush_interval
        self.raise_exceptions = raise_exceptions
        self.dropcount = 0
        self.start_flush_thread()

    def start_flush_thread(self):
        self.flush_thread = threading.Thread(
            target=_flush_worker,
            args=(threading.currentThread(),
                  self.uploader,
                  self.queue,
                  self.buffer_capacity,
                  self.flush_interval)
        )
        self.flush_thread.start()

    def emit(self, record):
        try:
            if not self.flush_thread.is_alive():
                self.start_flush_thread()
            payload = _create_payload(self, record)
            try:
                self.queue.put(payload, block=(not self.drop_extra_events))
            except queue.Full:
                self.dropcount += 1
                # Only raised when not blocking, which means that extra events
                # should be dropped.
                pass
        except Exception as e:
            if self.raise_exceptions:
                raise e

def _flush_worker(parent_thread, upload, pipe, buffer_capacity,
                  flush_interval):
    while True:
        last_flush = time.time()
        timeout = flush_interval
        log_buffer = []
        # If the parent thread has exited but there are still outstanding
        # events, attempt to send them before exiting.
        shutdown = not parent_thread.is_alive()

        # Fill phase: take events out of the queue and group them for sending.
        # Takes up to `buffer_capacity` events out of the queue and groups them
        # for sending; may send fewer than `buffer_capacity` events if
        # `flush_interval` seconds have passed without sending any events.
        while len(log_buffer) < buffer_capacity and timeout > 0:
            try:
                # When not in the shutdown phase, this will block for up to
                # `timeout` seconds waiting for a new item to be placed in
                # `pipe`. On each loop `timeout` is set to be the remaining
                # time in the flush period, so that exactly as soon as the
                # timeout period is over any items in `log_buffer` will be
                # sent.
                item = pipe.get(block=(not shutdown), timeout=timeout)
                log_buffer.append(item)
                pipe.task_done()
            except queue.Empty:
                # queue.Empty is raised if the timeout expires before a new
                # item is placed into the queue, or if a nonblocking `.get`
                # finds nothing in the queue. In the former case, the flush
                # interval has expired and the worker should flush any
                # outstanding events. In the latter case, there are no more
                # events to be sent and the worker should flush any outstanding
                # events. In both cases, we break this loop and continue to the
                # send phase.
                break
            timeout = _calculate_timeout(last_flush, flush_interval)

        # Send phase: takes the outstanding events (up to `buffer_capacity`
        # count) and sends them to the Timber endpoint all at once. If the
        # request fails in a way that can be retried, it is retried with an
        # exponential backoff in between attempts.
        if log_buffer:
            for delay in RETRY_SCHEDULE + (None,):
                response = upload(*log_buffer)
                if not _should_retry(response.status_code):
                    break
                if delay is not None:
                    time.sleep(delay)

        if shutdown:
            # In the case of a shutdown, every single event should already have
            # been pulled from `pipe`, placed in `log_buffer`, and sent.
            assert pipe.qsize() == 0
            sys.exit(0)


def _calculate_timeout(last_flush, flush_interval):
    elapsed = time.time() - last_flush
    timeout = max(flush_interval - elapsed, 0)
    return timeout


def _make_uploader(endpoint, api_key):
    headers = {
        'Authorization': 'Basic %s' % (
            base64.encodestring(api_key).replace('\n', ''),
        ),
        'Content-Type': 'application/json',
    }
    def upload(*payloads):
        data = json.dumps(payloads, indent=2)
        return requests.post(endpoint, data=data, headers=headers)
    return upload


def _create_payload(handler, record):
    r = record.__dict__
    payload = {}
    payload['dt'] = datetime.fromtimestamp(r['created']).isoformat()
    payload['level'] = level = _levelname(r['levelname'])
    payload['severity'] = r['levelno'] / 10
    payload['message'] = handler.format(record)
    payload['context'] = ctx = {}

    # Runtime context
    ctx['runtime'] = runtime = {}
    runtime['function'] = r['funcName']
    runtime['file'] = r['filename']
    runtime['line'] = r['lineno']

    # Custom context
    if handler.context.exists():
        ctx['custom'] = handler.context.collapse()

    events = _parse_custom_events(record)
    if events:
        payload['event'] = {'custom': events}

    return payload


def _levelname(level):
    return {
        'debug': 'debug',
        'info': 'info',
        'warning': 'warn',
        'error': 'error',
        'critical': 'critical',
    }[level.lower()]


def _parse_custom_events(record):
    default_keys = {
        'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
        'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
        'message', 'msg', 'name', 'pathname', 'process', 'processName',
        'relativeCreated', 'thread', 'threadName'
    }
    events = {}
    for key, val in record.__dict__.items():
        if key not in default_keys and isinstance(val, dict):
            events[key] = val
    return events


def _should_retry(status_code):
    return 500 <= status_code < 600
