# coding: utf-8
from __future__ import print_function, unicode_literals
import base64
import msgpack
import requests


class Uploader(object):
    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint
        auth_phrase = (
            base64
            .encodestring(api_key.encode('utf-8'))
            .decode('utf-8')
            .replace('\n', '')
        )
        self.headers = {
            'Authorization': 'Basic %s' % (auth_phrase),
            'Content-Type': 'application/msgpack',
        }

    def __call__(self, frame):
        data = msgpack.packb(frame, use_bin_type=True)
        return requests.post(self.endpoint, data=data, headers=self.headers)
