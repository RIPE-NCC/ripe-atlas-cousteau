import re
import mock
import unittest
import urlparse
from datetime import datetime, timedelta

from jsonschema import validate

from ripe.atlas.cousteau import (
    Ping,
    AtlasSource, AtlasChangeSource,
    AtlasCreateRequest, AtlasChangeRequest,
    AtlasResultsRequest, RequestGenerator, ProbeRequest,
    Probe, Measurement
)
from ripe.atlas.cousteau.exceptions import APIResponseError
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
        parsed_url = urlparse.urlparse(self.request.url_path)
        self.assertEqual(
            parsed_url.path, "/api/v1/measurement/1000002/result/"
        )
        query_filters = urlparse.parse_qs(parsed_url.query)
        self.assertTrue(set(
            query_filters.keys()
        ).issubset(["start", "stop", "prb_id"]))
        self.assertTrue(re.match(r"^\d+$", query_filters["start"][0]))
        self.assertTrue(re.match(r"^\d+$", query_filters["stop"][0]))
        self.assertTrue(
            re.match(r"^(\d+,)+\d+$", query_filters["prb_id"][0])
        )


class TestRequestGenerator(unittest.TestCase):
    def test_build_url(self):
        kwargs = {"limit": "100", "asn": "3333"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?limit=100&asn=3333"
        )
        kwargs = {"limit": "100", "asn": "3333", "tags": "NAT,system-ipv4-works"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?limit=100&tags=NAT,system-ipv4-works&asn=3333"
        )
        kwargs = {"asn": "3333"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?limit=300&asn=3333"
        )
        kwargs = {"limit": "10"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?limit=10"
        )
        kwargs = {}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?limit=300"
        )

    def test_generator(self):
        arequest = mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get').start()
        arequest.return_value = True, {
            "meta": {
                "total_count": "3",
                "use_iso_time": False,
                "next": None,
                "limit": 100,
                "offset": 0,
                "previous": None
            },
            "objects": [
                {
                    "address_v4": None,
                    "address_v6": None,
                    "asn_v4": None,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 90,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v4": None,
                    "prefix_v6": None,
                    "status": 3,
                    "tags": [
                        "home",
                        "nat",
                    ],
                    "latitude": 37.4675,
                    "longitude": 22.4015,
                    "status_name": "Abandoned",
                    "status_since": 1376578323
                },
                {
                    "asn_v4": 3329,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 268,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v6": None,
                    "status": 1,
                    "tags": [
                        "system-ipv6-ula",
                        "system-ipv4-rfc1918"
                    ],
                    "latitude": 40.6415,
                    "longitude": 22.9405,
                    "status_name": "Connected",
                    "status_since": 1433248709
                }
            ]
        }
        probe_generator = ProbeRequest(**{})
        probes_list = list(probe_generator)
        expected_value = [
            {
                "address_v4": None,
                "address_v6": None,
                "asn_v4": None,
                "asn_v6": None,
                "country_code": "GR",
                "id": 90,
                "is_anchor": False,
                "is_public": False,
                "prefix_v4": None,
                "prefix_v6": None,
                "status": 3,
                "tags": [
                    "home",
                    "nat",
                ],
                "latitude": 37.4675,
                "longitude": 22.4015,
                "status_name": "Abandoned",
                "status_since": 1376578323
            },
            {
                "asn_v4": 3329,
                "asn_v6": None,
                "country_code": "GR",
                "id": 268,
                "is_anchor": False,
                "is_public": False,
                "prefix_v6": None,
                "status": 1,
                "tags": [
                    "system-ipv6-ula",
                    "system-ipv4-rfc1918"
                ],
                "latitude": 40.6415,
                "longitude": 22.9405,
                "status_name": "Connected",
                "status_since": 1433248709
            }
        ]

        self.assertEqual(probes_list, expected_value)
        self.assertEqual(probe_generator.total_count, "3")

    def tearDown(self):
        mock.patch.stopall()


class TestProbeRepresentation(unittest.TestCase):
    def test_sane_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            resp = {
                "address_v4": "62.194",
                "address_v6": None,
                "asn_v4": 68,
                "asn_v6": None,
                "country_code": "ND",
                "id": 1,
                "is_anchor": False,
                "is_public": False,
                "prefix_v4": "62.194.0.0/16",
                "prefix_v6": None,
                "status": 1,
                "tags": ["cable"],
                "latitude": 52.3875,
                "longitude": 4.8875,
                "status_name": "Connected",
                "status_since": 1443446716
            }
            request_mock.return_value = True, resp
            probe = Probe(id=1)
            self.assertEqual(probe.meta_data, resp)
            self.assertEqual(probe.country_code, "ND")
            self.assertEqual(probe.address_v4, "62.194")
            self.assertEqual(probe.address_v6, None)
            self.assertEqual(probe.asn_v4, 68)
            self.assertEqual(probe.asn_v6, None)
            self.assertEqual(probe.is_anchor, False)
            self.assertEqual(probe.is_public, False)
            self.assertEqual(probe.prefix_v4, "62.194.0.0/16")
            self.assertEqual(probe.prefix_v6, None)
            self.assertEqual(probe.status, "Connected")
            self.assertEqual(probe.prefix_v6, None)
            self.assertEqual(probe.geometry, (52.3875, 4.8875))

    def test_error_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = False, {}
            self.assertRaises(APIResponseError, lambda: Probe(id=1))


class TestMeasurementRepresentation(unittest.TestCase):
    def test_sane_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            resp = {
                "af": 4,
                "dst_addr": "202.73.56.70",
                "dst_asn": 9255,
                "dst_name": "blaaaah",
                "msm_id": 2310448,
                "description": "Blaaaaaaaaaah",
                "is_oneoff": True,
                "is_public": True,
                "interval": 1800,
                "creation_time": 1439379910,
                "resolve_on_probe": False,
                "start_time": 1439379910,
                "stop_time": 1439380502,
                "status": {"id": 4, "name": "Stopped"},
                "resolved_ips": ["202.73.56.70"],
                "type": {"id": 8, "name": "http", "af": 4},
                "result": "/api/v1/measurement/2310448/result/"
            }
            request_mock.return_value = True, resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.meta_data, resp)
            self.assertEqual(measurement.protocol, 4)
            self.assertEqual(measurement.destination_address, "202.73.56.70")
            self.assertEqual(measurement.destination_asn, 9255)
            self.assertEqual(measurement.destination_name, "blaaaah")
            self.assertEqual(measurement.description, "Blaaaaaaaaaah")
            self.assertEqual(measurement.is_oneoff, True)
            self.assertEqual(measurement.is_public, True)
            self.assertEqual(measurement.interval, 1800)
            self.assertEqual(measurement.status, "Stopped")
            self.assertEqual(measurement.creation_time, datetime.fromtimestamp(1439379910))
            self.assertEqual(measurement.start_time, datetime.fromtimestamp(1439379910))
            self.assertEqual(measurement.stop_time, datetime.fromtimestamp(1439380502))
            self.assertEqual(measurement.type, "HTTP")
            self.assertEqual(measurement.result_url, "/api/v1/measurement/2310448/result/")

    def test_error_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = False, {}
            self.assertRaises(APIResponseError, lambda: Measurement(id=1))
