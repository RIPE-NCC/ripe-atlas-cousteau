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

# Python 3.4+ comes with mock in unittest
try:
    from unittest import mock
except ImportError:
    import mock
from unittest import TestCase
from datetime import datetime
from dateutil.tz import tzutc

from ripe.atlas.cousteau import Probe, Measurement
from ripe.atlas.cousteau.exceptions import APIResponseError


class TestProbeRepresentation(TestCase):
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
                "tags": ["cable"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.8875, 52.3875]
                },
                "status": {
                    "since": "2015-09-28T13:25:16",
                    "id": 1,
                    "name": "Connected"
                }
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
            self.assertEqual(probe.tags, ["cable"])
            self.assertEqual(probe.prefix_v6, None)
            self.assertEqual(probe.geometry, {"type": "Point", "coordinates": [4.8875, 52.3875]})

    def test_error_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = False, {}
            self.assertRaises(APIResponseError, lambda: Probe(id=1))

    def test_user_agent(self):

        paths = {
            "fetch": "ripe.atlas.cousteau.Probe._fetch_meta_data",
            "populate": "ripe.atlas.cousteau.Probe._populate_data",
        }

        with mock.patch(paths["fetch"]) as fetch:
            fetch.return_value = True
            with mock.patch(paths["populate"]):
                self.assertEqual(Probe(id=1)._user_agent, None)
                self.assertEqual(
                    Probe(id=1, user_agent=None)._user_agent, None)
                self.assertEqual(
                    Probe(id=1, user_agent="w00t")._user_agent, "w00t")

    def test_fields(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = True, {}
            Probe(id=1, fields=["probes"])
            self.assertEquals(request_mock.call_args[1], {"fields": "probes"})
            Probe(id=1, fields=["probes", "data"])
            self.assertEquals(request_mock.call_args[1], {"fields": "probes,data"})
            Probe(id=1, fields="probes,data")
            self.assertEquals(request_mock.call_args[1], {"fields": "probes,data"})
            Probe(id=1, fields=1)
            self.assertEquals(request_mock.call_args[1], {})


class TestMeasurementRepresentation(TestCase):

    def setUp(self):
        self.resp = {
            "af": 4,
            "target_ip": "202.73.56.70",
            "target_asn": 9255,
            "target": "blaaaah",
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

    def test_sane_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = True, self.resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.meta_data, self.resp)
            self.assertEqual(measurement.protocol, 4)
            self.assertEqual(measurement.target_ip, "202.73.56.70")
            self.assertEqual(measurement.target_asn, 9255)
            self.assertEqual(measurement.target, "blaaaah")
            self.assertEqual(measurement.description, "Blaaaaaaaaaah")
            self.assertEqual(measurement.is_oneoff, True)
            self.assertEqual(measurement.is_public, True)
            self.assertEqual(measurement.interval, 1800)
            self.assertEqual(measurement.status, "Stopped")
            self.assertEqual(measurement.creation_time, datetime.utcfromtimestamp(1439379910).replace(tzinfo=tzutc()))
            self.assertEqual(measurement.start_time, datetime.utcfromtimestamp(1439379910).replace(tzinfo=tzutc()))
            self.assertEqual(measurement.stop_time, datetime.utcfromtimestamp(1439380502).replace(tzinfo=tzutc()))
            self.assertEqual(measurement.type, "HTTP")
            self.assertEqual(measurement.result_url, "/api/v1/measurement/2310448/result/")

    def test_type1(self):
        """Tests format of the type key in response, soon to be deprecated."""
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            self.resp["type"] = {"id": 8, "name": "dns", "af": 4}
            request_mock.return_value = True, self.resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.type, "DNS")

            self.resp["type"] = {}
            request_mock.return_value = True, self.resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.type, "")

    def test_type2(self):
        """Tests new format of the type key in response, soon to be enabled."""
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            self.resp["type"] = "dns"
            request_mock.return_value = True, self.resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.type, "dns")

    def test_error_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = False, {}
            self.assertRaises(APIResponseError, lambda: Measurement(id=1))

    def test_user_agent(self):

        paths = {
            "fetch": "ripe.atlas.cousteau.Measurement._fetch_meta_data",
            "populate": "ripe.atlas.cousteau.Measurement._populate_data",
        }

        with mock.patch(paths["fetch"]) as fetch:
            fetch.return_value = True
            with mock.patch(paths["populate"]):
                self.assertEqual(Measurement(id=1)._user_agent, None)
                self.assertEqual(
                    Measurement(id=1, user_agent=None)._user_agent, None)
                self.assertEqual(
                    Measurement(id=1, user_agent="w00t")._user_agent, "w00t")

    def test_fields(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = True, {}
            Measurement(id=1, fields=["probes"])
            self.assertEquals(request_mock.call_args[1], {"fields": "probes"})
            Measurement(id=1, fields=["probes", "data"])
            self.assertEquals(request_mock.call_args[1], {"fields": "probes,data"})
            Measurement(id=1, fields="probes,data")
            self.assertEquals(request_mock.call_args[1], {"fields": "probes,data"})
            Measurement(id=1, fields=1)
            self.assertEquals(request_mock.call_args[1], {})

    def test_populate_times(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            del self.resp["stop_time"]
            del self.resp["creation_time"]
            del self.resp["start_time"]
            request_mock.return_value = True, self.resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.stop_time, None)
            self.assertEqual(measurement.start_time, None)
            self.assertEqual(measurement.creation_time, None)
