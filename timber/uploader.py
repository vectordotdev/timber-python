# coding: utf-8
from __future__ import print_function, unicode_literals
import base64
import json
import requests


class Uploader(object):
    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.api_key = api_key
        self.headers = {
            'Authorization': 'Basic %s' % (
                base64.encodestring(api_key).replace('\n', ''),
            ),
            'Content-Type': 'application/json',
        }

    def __call__(self, *payloads):
        data = json.dumps(payloads, indent=2)
        return requests.post(self.endpoint, data=data, headers=self.headers)
