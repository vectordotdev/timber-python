# coding: utf-8
from __future__ import print_function, unicode_literals
from functools import wraps


from timber.constants import TIMBER_CONTEXT_KEY


def _collapse_contexts(fn):
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        x = {}
        for contexts in self.extras:
            for name, data in contexts.items():
                x.setdefault(name, {}).update(data)
        if 'extra' in kwargs:
            x.setdefault('extra', {}).update(kwargs['extra'])
        if x:
            kwargs.setdefault('extra', {})[TIMBER_CONTEXT_KEY] = x
        return fn(self, *args, **kwargs)
    return wrapped


class ContextLogger(object):
    def __init__(self, logger, api_key):
        self.logger = logger
        self.extras = []

    def context(self, **kwargs):
        self.extras.append(kwargs)
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
