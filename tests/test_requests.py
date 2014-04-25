import unittest

from jsonschema import validate
from datetime import datetime, timedelta

from ripeatlas.measurement import Ping
from ripeatlas.source import AtlasSource, AtlasChangeSource
from ripeatlas.request import AtlasCreateRequest, AtlasChangeRequest
from . import post_data_create_schema, post_data_change_schema


class TestAtlasRequest(unittest.TestCase):

    def setUp(self):
        self.create_source = AtlasSource(
            **{"type": "area", "value": "WW", "requested": 3}
        )
        self.change_source = AtlasChangeSource(
            **{"value": "3,4", "requested": 3, "action": "add"}
        )
        self.measurement = Ping(**{
            "target": "testing", "af": 6,
            "description": "testing"
        })

    def test_url_build(self):
        request = AtlasCreateRequest(**{
            "measurements": [self.measurement], "sources": [self.create_source]
        })
        self.assertNotEquals(getattr(request, "url", None), None)


class TestAtlasCreateRequest(unittest.TestCase):
    def setUp(self):
        create_source = AtlasSource(
            **{"type": "area", "value": "WW", "requested": 3}
        )
        measurement = Ping(**{
            "target": "testing", "af": 6,
            "description": "testing"
        })
        self.request = AtlasCreateRequest(**{
            "start_time": datetime.utcnow(),
            "stop_time": datetime.utcnow() + timedelta(hours=2),
            "key": "path_to_key",
            "measurements": [measurement],
            "sources": [create_source]
        })

    def test_construct_post_data(self):
        self.request._construct_post_data()
        validate(self.request.post_data, post_data_create_schema)


class TestAtlasChangeRequest(unittest.TestCase):
    def setUp(self):
        change_source = AtlasChangeSource(
            **{"value": "3,4", "requested": 3, "action": "add"}
        )
        self.request = AtlasChangeRequest(**{
            "msm_id": 1, "sources": [change_source]
        })

    def test_construct_post_data(self):
        self.request._construct_post_data()
        validate(self.request.post_data, post_data_change_schema)
