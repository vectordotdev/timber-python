# coding: utf-8
from __future__ import print_function, unicode_literals
from timber.helpers import TimberContext


# TODO: change how this works
class Default(object):
    endpoint = 'https://logs.timber.io/frames'
    buffer_capacity = 1000  # log records
    flush_interval = 30  # seconds
    raise_exceptions = False
    drop_extra_events = True
    context = TimberContext()
