# coding: utf-8
from __future__ import print_function, unicode_literals
import json
import jsonschema
import os

_schema_url = (
    'https://raw.githubusercontent.com/'
    'timberio/log-event-json-schema/v4.0.1/schema.json'
)
_timber_root = os.path.dirname(os.path.abspath(__file__))
_schema_path = os.path.join(_timber_root, 'schema.json')
_schema = None


def _load_schema():
    global _schema
    if _schema is None:
        with open(_schema_path, 'r') as fin:
            _schema = json.load(fin)
    return _schema


def validate(data):
    schema = _load_schema()
    error = None
    try:
        jsonschema.validate(data, schema)
        data['$schema'] = _schema_url  # Gets added after validation?
    except jsonschema.exceptions.ValidationError as e:
        error = e
    return error
