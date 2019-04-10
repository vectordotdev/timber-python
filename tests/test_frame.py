# coding: utf-8

from timber.frame import create_frame
from timber.handler import TimberHandler
from timber.helpers import TimberContext
import unittest2
import logging

class TestTimberLogEntry(unittest2.TestCase):
    def test_create_frame_happy_path(self):
        handler = TimberHandler(api_key="some-api-key", source_id="some-source-id")
        log_record = logging.LogRecord("timber-test", 20, "/some/path", 10, "Some log message", [], None)
        frame = create_frame(log_record, log_record.getMessage(), TimberContext())
        self.assertTrue(frame['level'] == 'info')

    def test_create_frame_with_extra(self):
        handler = TimberHandler(api_key="some-api-key", source_id="some-source-id")

        log_record = logging.LogRecord("timber-test", 20, "/some/path", 10, "Some log message", [], None)
        extra = {'non_dict_key': 'string_value', 'dict_key': {'name': 'Test Test'}}
        log_record.__dict__.update(extra) # This is how `extra` gets included in the LogRecord

        # By default, non-dict keys are excluded.
        frame = create_frame(log_record, log_record.getMessage(), TimberContext())
        self.assertTrue(frame['level'] == 'info')
        self.assertIn('dict_key', frame)
        self.assertNotIn('non_dict_key', frame)

        frame = create_frame(log_record, log_record.getMessage(), TimberContext(), include_all_extra=True)
        self.assertIn('non_dict_key', frame)
