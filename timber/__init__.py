# coding: utf-8
from __future__ import print_function, unicode_literals
from logging import Handler, Formatter, NOTSET
import base64
import json
import requests
import pdb
from timber.schema import validate
from datetime import datetime

from timber.helpers import _debug
from timber.context import ContextLogger
from timber.constants import TIMBER_CONTEXT_KEY


def _context_from_record(record):
    return record.__dict__.get(TIMBER_CONTEXT_KEY, None)


def _create_payload(record):
    payload = {}
    record_dict = record.__dict__

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
    custom_context = _context_from_record(record)
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
