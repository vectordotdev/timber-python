# coding: utf-8
from __future__ import print_function, unicode_literals


class TimberContext(object):
    def __init__(self):
        self.extras = []

    def context(self, **kwargs):
        self.extras.append(kwargs)
        return self

    def __call__(self, **kwargs):
        return self.context(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is not None:
            return False
        self.extras.pop()
        return self

    def exists(self):
        return bool(self.extras)

    def collapse(self):
        x = {}
        for contexts in self.extras:
            for name, data in contexts.items():
                x.setdefault(name, {}).update(data)
        return x
