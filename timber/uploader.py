# coding: utf-8
from __future__ import print_function, unicode_literals
import base64
import msgpack
import requests


class Uploader(object):
    def __init__(self, api_key, source_id, host):
        self.api_key = api_key
        self.source_id = source_id
        self.host = host
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
        endpoint = self.host + '/sources/' + self.source_id + '/frames'
        data = msgpack.packb(frame, use_bin_type=True)
        return requests.post(endpoint, data=data, headers=self.headers)
