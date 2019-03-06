# coding: utf-8
from __future__ import print_function, unicode_literals
import msgpack
import mock
import unittest2

from timber.uploader import Uploader


class TestUploader(unittest2.TestCase):
    host = 'https://timber.io'
    source_id = 'dummy_source_id'
    api_key = 'dummy_api_key'
    frame = [1, 2, 3]

    @mock.patch('timber.uploader.requests.post')
    def test_call(self, post):
        def mock_post(endpoint, data=None, headers=None):
            # Check that the data is sent to ther correct endpoint
            self.assertEqual(endpoint, self.host + '/sources/' + self.source_id + '/frames')
            # Check the content-type
            self.assertIsInstance(headers, dict)
            self.assertIn('Authorization', headers)
            self.assertEqual('application/msgpack', headers.get('Content-Type'))
            # Check the content was msgpacked correctly
            self.assertEqual(msgpack.unpackb(data, raw=False), self.frame)

        post.side_effect = mock_post
        u = Uploader(self.api_key, self.source_id, self.host)
        u(self.frame)

        self.assertTrue(post.called)
