# coding: utf-8

from timber.frame import create_frame
from timber.handler import TimberHandler
from timber.helpers import TimberContext
import unittest2
import logging

class TestTimberLogEntry(unittest2.TestCase):
    def test_create_frame(self):
        handler = TimberHandler(api_key="some-api-key", source_id="some-source-id")
        log_record = logging.LogRecord("timber-test", 20, "/some/path", 10, "Some log message", [], None)
        frame = create_frame(log_record, log_record.getMessage(), TimberContext())
        self.assertTrue(frame['level'] == 'info')
