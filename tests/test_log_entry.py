# coding: utf-8

from timber.log_entry import create_log_entry
from timber.handler import TimberHandler
import unittest2
import logging

class TestTimberLogEntry(unittest2.TestCase):
    def test_create_log_entry(self):
        handler = TimberHandler(api_key="some-api-key", source_id="some-source-id")
        log_record = logging.LogRecord("timber-test", 20, "/some/path", 10, "Some log message", [], None)
        log_entry = create_log_entry(handler, log_record)
        self.assertTrue(log_entry['level'] == 'info')

