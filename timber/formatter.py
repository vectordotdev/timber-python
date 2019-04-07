# coding: utf-8
from __future__ import print_function, unicode_literals
import logging
import json

from .helpers import DEFAULT_CONTEXT
from .frame import create_frame


class TimberFormatter(logging.Formatter):
    def __init__(self,
                 context=DEFAULT_CONTEXT,
                 json_default=None,
                 json_encoder=None):
        self.context = context
        self.json_default = json_default
        self.json_encoder = json_encoder

    def format(self, record):
        frame = create_frame(record, record.getMessage(), self.context)
        return json.dumps(frame, default=self.json_default, cls=self.json_encoder)
