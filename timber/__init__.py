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

from timber.constants import DEFAULT_BUFFER_CAPACITY
from timber.constants import DEFAULT_DROP_EXTRA_EVENTS
from timber.constants import DEFAULT_ENDPOINT
from timber.constants import DEFAULT_FLUSH_INTERVAL
from timber.constants import DEFAULT_RAISE_EXCEPTIONS
from timber.helpers import ContextStack
from timber.helpers import _debug
from timber.helpers import make_context
from timber.schema import validate


context = ContextStack()


class TimberHandler(logging.Handler):
    def __init__(self, api_key, endpoint=DEFAULT_ENDPOINT,
            buffer_capacity=DEFAULT_BUFFER_CAPACITY,
            flush_interval=DEFAULT_FLUSH_INTERVAL,
            raise_exceptions=DEFAULT_RAISE_EXCEPTIONS,
            drop_extra_events=DEFAULT_DROP_EXTRA_EVENTS,
            context=context,
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
        self.flush_thread = None

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
            if not self.flush_thread or not self.flush_thread.is_alive():
                self.start_flush_thread()
            payload = _create_payload(self, record)
            try:
                self.queue.put(payload, block=(not self.drop_extra_events))
            except queue.Full:
                # Only raised when not blocking, which means that extra events
                # should be dropped.
                pass
        except Exception as e:
            if self.raise_exceptions:
                raise e


def _can_retry(status_code):
    return 500 <= status_code < 600


def _flush_worker(parent_thread, upload, in_queue, buffer_capacity, flush_interval):
    # TODO: make this an argument or move to constant
    retry_schedule = [1,10,60] # seconds

    last_flush = time.time()
    to_send = []
    shutdown = False

    while True:
        # If the parent thread has exited but there are still outstanding events,
        # attempt to send them before exiting.
        if not parent_thread.is_alive():
            shutdown = True

        # Fill phase: take events out of the queue and group them for sending.
        # Done one-at-a-time so that once `buffer_capacity` events have been
        # taken they're guaranteed to be sent.
        try:
            do_send = False
            reasons = []
            if shutdown:
                do_send = True
                reasons.append('shutdown')
            if in_queue.full():
                do_send = True
                reasons.append('full queue')
            if time.time() - last_flush > flush_interval:
                do_send = True
                reasons.append('flush interval expired')
            if not do_send:
                continue # To top of loop
            to_send = []
            while len(to_send) < buffer_capacity:
                item = in_queue.get(block=False)
                to_send.append(item)
                in_queue.task_done()
        except queue.Empty:
            pass

        if shutdown and not to_send:
            assert not to_send
            assert not in_queue.qsize()
            sys.exit(0)

        _debug('sending because', reasons)
        # Send phase: takes the outstanding events (up to `buffer_capacity`
        # count) and sends them to the Timber endpoint all at once. If the
        # request fails in a way that can be retried, it is retried with an
        # exponential backoff in between attempts.
        for delay in retry_schedule:
            response = upload(*to_send)
            last_flush = time.time()
            if not _can_retry(response.status_code):
                _debug(len(to_send), response.status_code, response.content)
                break
            time.sleep(delay)


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

    error = validate(payload)
    if error is not None:
        raise error

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
    default_keys = { 'args', 'asctime', 'created', 'exc_info', 'exc_text',
    'filename', 'funcName', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process', 'processName',
    'relativeCreated', 'thread', 'threadName'}
    events = {}
    for key, val in record.__dict__.items():
        if key not in default_keys and isinstance(val, dict):
            events[key] = val
    return events
