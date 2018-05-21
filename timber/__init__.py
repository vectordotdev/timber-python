# coding: utf-8
from __future__ import print_function, unicode_literals
import base64
import json
import logging
import queue
import requests
import time
import time
from datetime import datetime
from threading import Thread

from timber.constants import DEFAULT_ENDPOINT, DEFAULT_BUFFER_CAPACITY, DEFAULT_FLUSH_INTERVAL, DEFAULT_RAISE_EXCEPTIONS
from timber.helpers import ContextStack, make_context, _debug
from timber.schema import validate


context = ContextStack()


class TimberHandler(logging.Handler):
    def __init__(self, api_key, endpoint=DEFAULT_ENDPOINT, buffer_capacity=DEFAULT_BUFFER_CAPACITY, flush_interval=DEFAULT_FLUSH_INTERVAL, context=context, raise_exceptions=DEFAULT_RAISE_EXCEPTIONS, level=logging.NOTSET):
        super(TimberHandler, self).__init__(level=level)
        self.api_key = api_key
        self.endpoint = endpoint
        self.context = context
        self.queue = queue.Queue()
        self.uploader = _make_uploader(self.endpoint, self.api_key)
        self.buffer_capacity = buffer_capacity
        self.flush_interval = flush_interval
        self.raise_exceptions = raise_exceptions
        self.flush_thread = None

    def start_flush_thread(self):
        self.flush_thread = Thread(
            target=_flush_worker,
            args=(self.uploader,
                  self.queue,
                  self.buffer_capacity,
                  self.flush_interval)
        )
        self.flush_thread.daemon = True
        self.flush_thread.start()

    def emit(self, record):
        try:
            if not self.flush_thread or not self.flush_thread.is_alive():
                self.start_flush_thread()
            payload = _create_payload(self, record)
            if payload is not None:
                self.queue.put(payload)
        except Exception as e:
            if self.raise_exceptions:
                raise e


def _flush_worker(upload, in_queue, buffer_capacity, flush_interval):
    last_flush = time.time()
    out_queue = []
    retry_count = 0

    while True:
        if ((time.time() - last_flush >= flush_interval and len(out_queue) > 0)
                or len(out_queue) >= buffer_capacity):
            to_send = out_queue
            out_queue = []
            # TODO: check response and do exponential backoff up to 3 times
            response = upload(*to_send)
            _debug(response.status_code, response.content)
            last_flush = time.time()
        try:
            timeout = max(flush_interval - (time.time() - last_flush), 0)
            item = in_queue.get(block=True, timeout=timeout)
            out_queue.append(item)
            in_queue.task_done()
        except queue.Empty:
            pass


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
    if level is None:
        return None

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
    }.get(level.lower(), None)


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
