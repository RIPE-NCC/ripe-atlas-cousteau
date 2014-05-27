import re
import unittest
import urlparse
from datetime import datetime, timedelta

from jsonschema import validate

from ripe.atlas.cousteau import (
    Ping,
    AtlasSource, AtlasChangeSource,
    AtlasCreateRequest, AtlasChangeRequest,
    AtlasResultsRequest
)
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
        request.build_url()
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


class TestAtlasResultsRequest(unittest.TestCase):
    def setUp(self):
        self.request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27",
            "stop": "2011-11-27 01",
            "probe_ids": [1, 2, 3]
        })

    def test_url_path(self):
        #self.request.construct_url_path()
        parsed_url = urlparse.urlparse(self.request.url_path)
        self.assertEqual(
            parsed_url.path, "/api/v1/measurement/1000002/result/"
        )
        print urlparse.parse_qs(parsed_url.query)
        query_filters = urlparse.parse_qs(parsed_url.query)
        self.assertTrue(set(
            query_filters.keys()
        ).issubset(["start", "stop", "prb_id"]))
        print re.match("^/d+$", query_filters["start"][0])
        print query_filters["start"][0]
        self.assertTrue(re.match(r"^\d+$", query_filters["start"][0]))
        self.assertTrue(re.match(r"^\d+$", query_filters["stop"][0]))
        self.assertTrue(
            re.match(r"^(\d+,)+\d+$", query_filters["prb_id"][0])
        )
