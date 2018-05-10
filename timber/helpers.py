# coding: utf-8
from __future__ import print_function, unicode_literals
import json

def _debug(*data):
    print(json.dumps(data, indent=2, sort_keys=True))
