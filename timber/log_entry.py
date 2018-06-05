# coding: utf-8
from __future__ import print_function, unicode_literals
from datetime import datetime

SCHEMA_URL = (
    'https://raw.githubusercontent.com/'
    'timberio/log-event-json-schema/v4.0.1/schema.json'
)


def create_log_entry(handler, record):
    r = record.__dict__
    entry = {}
    entry['$schema'] = SCHEMA_URL
    entry['dt'] = datetime.fromtimestamp(r['created']).isoformat()
    entry['level'] = level = _levelname(r['levelname'])
    entry['severity'] = int(r['levelno'] / 10)
    entry['message'] = handler.format(record)
    entry['context'] = ctx = {}

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
        entry['event'] = {'custom': events}

    return entry


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
