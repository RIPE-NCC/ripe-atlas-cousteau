import os
import unittest
from datetime import datetime, timedelta
from collections import namedtuple

from nose.exc import SkipTest


from ripe.atlas.cousteau import (
    AtlasSource, AtlasChangeSource,
    AtlasRequest, AtlasCreateRequest, AtlasChangeRequest,
    Ping, Dns, AtlasStopRequest, AtlasResultsRequest,
    ProbeRequest, MeasurementRequest, Probe, Measurement,
    AtlasStream
)


class TestRealServer(unittest.TestCase):
    def setUp(self):
        self.server = os.environ.get('ATLAS_SERVER', "")
        self.create_key = os.environ.get('CREATE_KEY', "")
        self.change_key = os.environ.get('CHANGE_KEY', "")
        self.delete_key = os.environ.get('DELETE_KEY', "")
        self.delete_msm = None

    def test_create_delete_request(self):
        """Unittest for Atlas create and delete request"""
        if self.server == "":
            raise SkipTest
        source = AtlasSource(**{"type": "area", "value": "WW", "requested": 38})
        ping = Ping(**{
            "target": "www.google.fr",
            "af": 4,
            "description": "testing",
            "prefer_anchors": True
        })
        dns = Dns(**{
            "target": "k.root-servers.net", "af": 4,
            "description": "testing new wrapper", "query_type": "SOA",
            "query_class": "IN", "query_argument": "nl", "retry": 6
        })
        stop = datetime.utcnow() + timedelta(minutes=220)
        request = AtlasCreateRequest(
            **{
                "stop_time": stop,
                "key": self.create_key,
                "server": self.server,
                "measurements": [ping, dns],
                "sources": [source]
            }
        )
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.create()
        self.delete_msm = result.response["measurements"][0]
        print result.response
        self.assertTrue(result.success)

        # Unittest for Atlas delete request
        if self.server == "":
            raise SkipTest

        kwargs = {"msm_id": self.delete_msm, "key": self.delete_key, "server": self.server}
        request = AtlasStopRequest(**kwargs)
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.create()
        print result.response
        self.assertTrue(result.success)

    def test_change_request(self):
        """Unittest for Atlas change request"""
        if self.server == "":
            raise SkipTest

        remove = AtlasChangeSource(**{
            "value": "6001", "requested": 1, "action": "remove", "type": "probes"
        })
        add = AtlasChangeSource(**{
            "value": "6002", "requested": 1, "action": "add", "type": "probes"
        })
        request = AtlasChangeRequest(
            **{
                "key": self.change_key,
                "msm_id": 1000032,
                "server": self.server,
                "sources": [add, remove]
            }
        )
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.create()
        self.assertTrue(result.success)

    def test_result_request(self):
        """Unittest for Atlas results request"""
        if self.server == "":
            raise SkipTest

        kwargs = {
            "msm_id": 1000032,
            "start": datetime(2011, 11, 21),
            "stop": datetime(2011, 11, 22),
            "probe_ids": [743, 630]
        }

        result = namedtuple('Result', 'success response')
        (result.success, result.response) = AtlasResultsRequest(**kwargs).create()
        print result.success, result.response
        self.assertTrue(result.response)
        self.assertTrue(result.success)

    def test_probe_request(self):
        """Unittest for ProbeRequest"""
        if self.server == "":
            raise SkipTest

        filters = {"tags": "NAT", "country_code": "NL", "asn_v4": "3333"}
        probes = ProbeRequest(**filters)
        probes_list = list(probes)
        self.assertTrue(probes_list)
        self.assertTrue(probes.total_count)

    def test_measurement_request(self):
        """Unittest for MeasurementRequest"""
        if self.server == "":
            raise SkipTest

        filters = {"status": 6}
        measurements = MeasurementRequest(**filters)
        measurements_list = list(measurements)
        self.assertTrue(measurements_list)
        self.assertTrue(measurements.total_count)

    def test_probe_repr_request(self):
        """Unittest for Probe representation request"""
        if self.server == "":
            raise SkipTest

        Probe(id=6001)

    def test_measurement_repr_request(self):
        """Unittest for Measurement representation request"""
        if self.server == "":
            raise SkipTest

        Measurement(id=1000032)

    def test_stream_request(self):
        """Unittest for Atlas results request"""
        if self.server == "":
            raise SkipTest

        results = []

        def on_result_response(*args):
            """
            Function that will be called every time we receive a new result.
            Args is a tuple, so you should use args[0] to access the real message.
            """
            results.append(args[0])

        atlas_stream = AtlasStream()
        atlas_stream.connect()
        stream_type = "result"
        atlas_stream.bind_stream(stream_type, on_result_response)
        stream_parameters = {"msm": 1001}
        atlas_stream.start_stream(stream_type=stream_type, **stream_parameters)
        atlas_stream.timeout(seconds=5)
        atlas_stream.disconnect()
        self.assertNotEqual(results, [])

    def test_get_request(self):
        """Unittest for Atlas get request"""
        if self.server == "":
            raise SkipTest

        request = AtlasRequest(
            **{
                "url_path": "/api/v2/anchors"
            }
        )
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.get()
        print result.success, result.response
        self.assertTrue(result.response["results"])
        self.assertTrue(result.success)
