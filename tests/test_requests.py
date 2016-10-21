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
import requests
from datetime import datetime

from jsonschema import validate

from ripe.atlas.cousteau.version import __version__
from ripe.atlas.cousteau import (
    Ping, AtlasSource, AtlasChangeSource, AtlasCreateRequest,
    AtlasChangeRequest, AtlasLatestRequest, AtlasResultsRequest,
    AtlasRequest
)
from . import post_data_create_schema, post_data_change_schema


class FakeResponse(object):
    def __init__(self, json_return={}, ok=True):
        self.json_return = json_return
        self.ok = ok
        self.text = "testing"

    def json(self):
        return self.json_return


class FakeErrorResponse(FakeResponse):
    def json(self):
        raise ValueError("json breaks")


class TestAtlasRequest(TestCase):
    def setUp(self):
        self.request = AtlasRequest(**{
            "key": "blaaaa",
            "server": "test",
            "url_path": "testing"
        })

    def test_headers(self):
        """Tests header fields of the request."""
        expected_output = {
            "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.assertEqual(expected_output, self.request.get_headers())

    def test_http_method_args(self):
        """Tests initial args that will be passed later to HTTP method."""
        expected_output = {
            "params": {"key": "blaaaa"},
            "verify": True,
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "proxies": {},
        }
        self.assertEqual(expected_output, self.request.http_method_args)

    def test_get_method(self):
        """Tests GET reuest method"""
        extra_params = {"bull": "shit", "cow": "shit", "horse": "shit"}
        expected_args = {
            "params": {
                "key": "blaaaa", "bull": "shit",
                "cow": "shit", "horse": "shit"
            },
            "verify": True,
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "proxies": {},
        }
        with mock.patch("ripe.atlas.cousteau.request.AtlasRequest.http_method") as mock_get:
            mock_get.return_value = True
            self.request.get(**extra_params)
            self.assertEqual(self.request.http_method_args, expected_args)

    def test_url_build(self):
        """Tests build of the url of the request."""
        self.request.build_url()
        self.assertEqual(self.request.url, "https://testtesting")

    def test_success_http_method(self):
        """Tests the main http method function of the request in case of success"""
        with mock.patch("ripe.atlas.cousteau.AtlasRequest.get_http_method") as mock_get:
            fake = FakeResponse(json_return={"blaaa": "b"})
            mock_get.return_value = fake
            self.assertEqual(
                self.request.http_method("GET"),
                (True, {"blaaa": "b"})
            )

            fake_error = FakeErrorResponse()
            mock_get.return_value = fake_error
            self.assertEqual(
                self.request.http_method("GET"),
                (True, "testing")
            )

    def test_not_success_http_method(self):
        """Tests the main http method function of the request in case of fail"""
        with mock.patch("ripe.atlas.cousteau.AtlasRequest.get_http_method") as mock_get:
            fake = FakeResponse(json_return={"blaaa": "b"}, ok=False)
            mock_get.return_value = fake
            self.assertEqual(
                self.request.http_method("GET"),
                (False, {"blaaa": "b"})
            )

            fake_error = FakeErrorResponse(ok=False)
            mock_get.return_value = fake_error
            self.assertEqual(
                self.request.http_method("GET"),
                (False, "testing")
            )

    def test_exception_http_method(self):
        """Tests the main http method function of the request in case of fail"""
        with mock.patch("ripe.atlas.cousteau.AtlasRequest.get_http_method") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("excargs")
            self.assertEqual(
                self.request.http_method("GET"),
                (False, ("excargs",))
            )

    def test_user_agent(self):
        with mock.patch("ripe.atlas.cousteau.request.__version__", 999):
            standard = "RIPE ATLAS Cousteau v999"
            self.assertEqual(AtlasRequest().http_agent, standard)
            self.assertEqual(AtlasRequest(user_agent=None).http_agent, standard)
            self.assertEqual(AtlasRequest(user_agent="w00t").http_agent, "w00t")


class TestAtlasCreateRequest(TestCase):
    def setUp(self):
        self.create_source = AtlasSource(
            **{"type": "area", "value": "WW", "requested": 3}
        )
        self.measurement = Ping(**{
            "target": "testing", "af": 6,
            "description": "testing"
        })
        self.request = AtlasCreateRequest(**{
            "start_time": datetime(2015, 10, 16),
            "stop_time": 1445040000,
            "key": "path_to_key",
            "measurements": [self.measurement],
            "sources": [self.create_source],
            "is_oneoff": True,
        })

    def test_construct_post_data(self):
        """Tests construction of past data"""
        self.request._construct_post_data()
        validate(self.request.post_data, post_data_create_schema)

    def test_post_method(self):
        """Tests POST reuest method"""
        self.maxDiff = None
        expected_args = {
            "json": {
                "definitions": [{
                    "af": 6, "description": "testing",
                    "target": "testing", "type": "ping"
                }],
                "is_oneoff": True,
                "probes": [{"requested": 3, "type": "area", "value": "WW"}],
                "start_time": 1444953600,
                "stop_time": 1445040000
            },
            "params": {"key": "path_to_key"},
            "verify": True,
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "proxies": {},
        }
        with mock.patch("ripe.atlas.cousteau.request.AtlasRequest.http_method") as mock_get:
            self.request._construct_post_data()
            mock_get.return_value = True
            self.request.post()
            self.assertEqual(self.request.http_method_args, expected_args)

    def test_post_method_without_times(self):
        """Tests POST reuest method without any time specified"""
        request = AtlasCreateRequest(**{
            "key": "path_to_key",
            "measurements": [self.measurement],
            "sources": [self.create_source],
        })
        self.maxDiff = None
        expected_args = {
            "json": {
                "definitions": [{
                    "af": 6, "description": "testing",
                    "target": "testing", "type": "ping"
                }],
                "is_oneoff": False,
                "probes": [{"requested": 3, "type": "area", "value": "WW"}],
            },
            "params": {"key": "path_to_key"},
            "verify": True,
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "proxies": {},
        }
        with mock.patch("ripe.atlas.cousteau.request.AtlasRequest.http_method") as mock_get:
            request._construct_post_data()
            mock_get.return_value = True
            request.post()
            self.assertEqual(request.http_method_args, expected_args)


class TestAtlasChangeRequest(TestCase):
    def setUp(self):
        change_source = AtlasChangeSource(
            **{"value": "WW", "requested": 3, "action": "add", "type": "area"}
        )
        self.request = AtlasChangeRequest(**{
            "msm_id": 1, "sources": [change_source]
        })

    def test_construct_post_data(self):
        self.request._construct_post_data()
        validate(self.request.post_data, post_data_change_schema)


class TestAtlasResultsRequest(TestCase):

    def test_url_path_and_params(self):
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27",
            "stop": "2011-11-27 01",
            "probe_ids": [1, 2, 3]
        })
        self.assertEqual(
            request.url_path, "/api/v2/measurements/1000002/results"
        )
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            set(query_filters.keys()), set(["key", "stop", "start", "probe_ids"])
        )
        self.assertEqual(query_filters["start"], 1322352000)
        self.assertEqual(query_filters["stop"], 1322355600)
        self.assertEqual(
            query_filters["probe_ids"], "1,2,3"
        )

    def test_probe_ids_query_params(self):
        """Tests probe_ids as query params for different entries"""
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "probe_ids": [1, 2, 3]
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            query_filters["probe_ids"], "1,2,3"
        )

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "probe_ids": "15,  2,3"
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            query_filters["probe_ids"], "15,  2,3"
        )

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "probe_ids": 15
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            query_filters["probe_ids"], 15
        )

    def test_start_time_query_params(self):
        """Tests start time as query params for different entries"""
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27 01:01",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322355660)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": 1322352000,
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": datetime(2011, 11, 27)
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322352000)

    def test_stop_time_query_params(self):
        """Tests stop time as query params for different entries"""
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": "2011-11-27",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": "2011-11-27 01:01",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322355660)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": 1322352000,
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": datetime(2011, 11, 27)
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322352000)


class TestAtlasLatestRequest(TestCase):

    def test_url_path(self):
        """Tests construction of path."""
        self.assertEqual(
            AtlasLatestRequest(msm_id=1001).url_path,
            "/api/v2/measurements/1001/latest"
        )
        self.assertEqual(
            AtlasLatestRequest(msm_id=1002, probe_ids=[1, 2, 3]).url_path,
            "/api/v2/measurements/1002/latest"
        )

    def test_query_params(self):
        """Tests construction of query parameters."""
        self.assertEqual(
            AtlasLatestRequest(
                msm_id=1001, probe_ids=(1, 2, 3, 24)
            ).http_method_args["params"],
            {"key": None, "probe_ids": "1,2,3,24"}
        )
        self.assertEqual(
            AtlasLatestRequest(
                msm_id=1001, probe_ids="1, 2, 3, 24"
            ).http_method_args["params"],
            {"key": None, "probe_ids": "1, 2, 3, 24"}
        )


class TestAtlasRequestCustomHeaders(TestCase):
    def setUp(self):
        self.create_source = AtlasSource(
            **{"type": "area", "value": "WW", "requested": 3}
        )
        self.measurement = Ping(**{
            "target": "testing", "af": 6,
            "description": "testing"
        })
        self.request = AtlasCreateRequest(**{
            "start_time": datetime(2015, 10, 16),
            "stop_time": 1445040000,
            "key": "path_to_key",
            "measurements": [self.measurement],
            "sources": [self.create_source],
            "is_oneoff": True,
            "headers": {"hello": "world"},
        })

    def test_custom_headers(self):
        expected_headers = {
            "Content-Type": "application/json",
            "hello": "world",
            "Accept": "application/json",
            "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__)
        }
        self.assertEqual(self.request.get_headers(), expected_headers)
