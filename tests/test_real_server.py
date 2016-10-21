# Copyright (c) 2015 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    AtlasStream, Ntp, Sslcert, Http, Traceroute, AnchorRequest
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
            "target": "www.ripe.net",
            "af": 4,
            "description": "Cousteau testing",
            "prefer_anchors": True
        })
        traceroute = Traceroute(**{
            "target": "www.google.fr",
            "af": 4, "protocol": "UDP",
            "description": "Cousteau testing",
            "dont_fragment": True
        })
        dns = Dns(**{
            "target": "k.root-servers.net", "af": 4,
            "description": "Cousteau testing", "query_type": "SOA",
            "query_class": "IN", "query_argument": "nl", "retry": 6
        })
        ntp = Ntp(**{
            "target": "www.ripe.net",
            "af": 4,
            "description": "Cousteau testing",
            "timeout": 1000
        })
        ssl = Sslcert(**{
            "target": "www.ripe.net",
            "af": 4,
            "description": "Cousteau testing",
        })
        http = Http(**{
            "target": "www.ripe.net",
            "af": 4,
            "description": "Cousteau testing",
        })
        stop = datetime.utcnow() + timedelta(minutes=220)
        request = AtlasCreateRequest(
            **{
                "verify": False,
                "stop_time": stop,
                "key": self.create_key,
                "server": self.server,
                "measurements": [ping, traceroute, dns, ntp, ssl, http],
                "sources": [source]
            }
        )
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.create()
        print(result.response)
        self.assertTrue(result.success)
        self.delete_msm = result.response["measurements"][0]
        self.assertTrue(result.success)

        # Unittest for Atlas delete request
        if self.server == "":
            raise SkipTest

        kwargs = {"verify": False, "msm_id": self.delete_msm, "key": self.delete_key, "server": self.server}
        request = AtlasStopRequest(**kwargs)
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.create()
        print(result.response)
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
                "verify": False,
                "msm_id": 1000032,
                "server": self.server,
                "sources": [add, remove]
            }
        )
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.create()
        print(result.response)
        self.assertTrue(result.success)

    def test_result_request(self):
        """Unittest for Atlas results request"""
        if self.server == "":
            raise SkipTest

        kwargs = {
            "msm_id": 1000032,
            "start": datetime(2011, 11, 21),
            "stop": datetime(2011, 11, 22),
            "verify": False,
            "probe_ids": [743, 630]
        }

        result = namedtuple('Result', 'success response')
        (result.success, result.response) = AtlasResultsRequest(**kwargs).create()
        print(result.success, result.response)
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

        filters = {"id__lt": 1000010, "id__gt": 1000002}
        measurements = MeasurementRequest(**filters)
        measurements_list = list(measurements)
        self.assertTrue(measurements_list)
        self.assertTrue(measurements.total_count)

    def test_anchor_request(self):
        """Unittest for AnchorRequest"""
        if self.server == "":
            raise SkipTest

        anchors = AnchorRequest()
        anchors_list = list(anchors)
        self.assertTrue(anchors_list)
        self.assertTrue(anchors.total_count)

    def test_probe_repr_request(self):
        """Unittest for Probe representation request"""
        if self.server == "":
            raise SkipTest

        Probe(id=6001)

    def test_measurement_repr_request(self):
        """Unittest for Measurement representation request"""
        if self.server == "":
            raise SkipTest

        Measurement(id=1000032, server=self.server, verify=False)

    def test_stream_results(self):
        """Unittest for Atlas results request."""
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
        channel = "result"
        atlas_stream.bind_channel(channel, on_result_response)
        stream_parameters = {"msm": 1001}
        atlas_stream.start_stream(stream_type="result", **stream_parameters)
        atlas_stream.timeout(seconds=5)
        atlas_stream.disconnect()
        self.assertNotEqual(results, [])

    def test_stream_probe(self):
        """Unittest for Atlas probe connections request."""
        if self.server == "":
            raise SkipTest

        results = []

        def on_result_response(*args):
            """
            Function that will be called every time we receive a new event.
            Args is a tuple, so you should use args[0] to access the real message.
            """
            results.append(args[0])

        atlas_stream = AtlasStream()
        atlas_stream.connect()
        channel = "atlas_probestatus"
        atlas_stream.bind_channel(channel, on_result_response)
        stream_parameters = {"enrichProbes": True}
        atlas_stream.start_stream(stream_type="probestatus", **stream_parameters)
        atlas_stream.timeout(seconds=30)
        atlas_stream.disconnect()
        self.assertNotEqual(results, [])

    def test_get_request(self):
        """Unittest for Atlas get request"""
        if self.server == "":
            raise SkipTest

        request = AtlasRequest(
            **{
                "verify": False,
                "url_path": "/api/v2/anchors"
            }
        )
        result = namedtuple('Result', 'success response')
        (result.success, result.response) = request.get()
        print(result.success, result.response)
        self.assertTrue(result.response["results"])
        self.assertTrue(result.success)
