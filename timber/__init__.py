# coding: utf-8
from __future__ import print_function, unicode_literals
from logging import Handler, Formatter, NOTSET
from functools import wraps
import base64
import json
import requests
import pdb
from timber.schema import validate
from datetime import datetime


def _debug(*data):
    print(json.dumps(data, indent=2, sort_keys=True))


def _collapse_contexts(fn):
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        x = {}
        for name, e in self.extras:
            x.setdefault(name, {}).update(e)
        if 'extra' in kwargs:
            x.setdefault('extra', {}).update(kwargs['extra'])
        if x:
            kwargs.setdefault('extra', {})['__timber_context'] = x
        return fn(self, *args, **kwargs)
    return wrapped


def _create_payload(record):
    payload = {}
    record_dict = record.__dict__
    pdb.set_trace()

    payload['dt'] = datetime.fromtimestamp(record_dict['created']).isoformat()
    payload['level'] = record_dict['levelname'].lower()
    payload['severity'] = record_dict['levelno'] / 10
    payload['time_ms'] = record_dict['msecs'] # XXX: is this what time_ms is supposed to be?
    payload['context'] = context = {}
    # Runtime context
    context['runtime'] = runtime = {}
    runtime['function'] = record_dict['funcName']
    runtime['file'] = record_dict['filename']
    runtime['line'] = record_dict['lineno']
    # Custom context
    custom_context = record_dict.get('__timber_context', None)
    if custom_context:
        context['custom'] = custom_context
    return payload


def _upload(endpoint, api_key, *payloads):
    headers = {
        'Authorization': 'Basic %s' % (
            base64.encodestring(api_key).replace('\n', ''),
        ),
        'Content-Type': 'application/json',
    }
    _debug(payloads)
    data = json.dumps(payloads, indent=2)
    return requests.post(endpoint, data=data, headers=headers)


class TimberHandler(Handler):
    def __init__(self, api_key, endpoint='https://logs.timber.io/frames', level=NOTSET):
        super(TimberHandler, self).__init__(level=level)
        self.api_key = api_key
        self.endpoint = endpoint

    def emit(self, record):
        payload = _create_payload(record)
        payload['message'] = self.format(record)
        error = validate(payload)
        if error is not None:
            raise error
        response = _upload(self.endpoint, self.api_key, payload)
        if response.status_code != 202:
            e = Exception(response.status_code)
            e.response = response
            raise e
        _debug(response.status_code, response.content)


class ContextLogger(object):
    def __init__(self, logger, api_key):
        self.logger = logger
        self.handler = TimberHandler(api_key)
        self.logger.addHandler(self.handler)
        self.extras = []

    def context(self, name, ctx):
        self.extras.append((name, ctx))
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is not None:
            return False
        self.extras.pop()
        return self

    @_collapse_contexts
    def critical(self, *args, **kwargs):
        return self.logger.critical(*args, **kwargs)
