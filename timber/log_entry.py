# coding: utf-8
from __future__ import print_function, unicode_literals
from datetime import datetime


def create_log_entry(handler, record):
    r = record.__dict__
    entry = {}
    entry['dt'] = datetime.utcfromtimestamp(r['created']).isoformat()
    entry['level'] = level = _levelname(r['levelname'])
    entry['severity'] = int(r['levelno'] / 10)
    entry['message'] = handler.format(record)
    entry['context'] = ctx = {}

    # Runtime context
    ctx['runtime'] = runtime = {}
    runtime['function'] = r['funcName']
    runtime['file'] = r['filename']
    runtime['line'] = r['lineno']
    runtime['thread_id'] = r['thread']
    runtime['thread_name'] = r['threadName']
    runtime['logger_name'] = r['name']

    # Runtime context
    ctx['system'] = system = {}
    system['pid'] = r['process']
    system['process_name'] = r['processName']

    # Custom context
    if handler.context.exists():
        ctx.update(handler.context.collapse())

    events = _parse_custom_events(record)
    if events:
        entry.update(events)

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
