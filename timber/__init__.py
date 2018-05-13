# coding: utf-8
from __future__ import print_function, unicode_literals
from logging import Logger, Handler, Formatter, NOTSET
import logging
import base64
import json
import requests
import pdb
from timber.schema import validate
from datetime import datetime

from timber.helpers import _debug, ContextStack
from timber.constants import DEFAULT_ENDPOINT


context = ContextStack()
event = ContextStack()


class TimberHandler(Handler):
    def __init__(self, api_key,  endpoint=DEFAULT_ENDPOINT, level=NOTSET):
        super(TimberHandler, self).__init__(level=level)
        self.api_key = api_key
        self.endpoint = endpoint

    def emit(self, record):
        payload = _create_payload(self, record)
        # TODO: instead of uploading directly, instantiate an uploading thread
        # and have the _upload function put all this data into a queue for
        # later processing.
        response = _upload(self.endpoint, self.api_key, payload)
        # TODO: handlers shouldn't raise unless asked to do so.
        if response.status_code != 202:
            e = Exception(response.status_code)
            e.response = response
            raise e
        _debug(response.status_code, response.content)


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


def _create_payload(handler, record):
    payload = {}
    record_dict = record.__dict__

    payload['dt'] = datetime.fromtimestamp(record_dict['created']).isoformat()
    payload['level'] = record_dict['levelname'].lower()
    payload['severity'] = record_dict['levelno'] / 10
    payload['message'] = handler.format(record)
    # TODO:  is this what time_ms is supposed to be?
    payload['time_ms'] = record_dict['msecs']
    payload['context'] = ctx = {}
    # Runtime context
    ctx['runtime'] = runtime = {}
    runtime['function'] = record_dict['funcName']
    runtime['file'] = record_dict['filename']
    runtime['line'] = record_dict['lineno']
    # Custo context
    if context.exists():
        ctx['custom'] = context.collapse()
    extra = _make_extra(record)
    if extra:
        ctx['custom'].setdefault('extra', {}).update(extra)
    # Custom event data
    if event.exists():
        payload['event'] = {'custom': event.collapse()}

    # TODO: how to handle events similarly to Ruby library?
    # https://timber.io/docs/languages/ruby/usage/custom-events/
    error = validate(payload)
    if error is not None:
        raise error
    return payload


def _make_extra(record):
    default_keys = { 'args', 'asctime', 'created', 'exc_info', 'exc_text',
    'filename', 'funcName', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process', 'processName',
    'relativeCreated', 'thread', 'threadName'}
    extra = {}
    for key, val in record.__dict__.items():
        if key  not in default_keys:
            extra[key] = val
    return extra

