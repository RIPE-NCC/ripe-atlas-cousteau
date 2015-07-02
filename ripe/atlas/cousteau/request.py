"""
Module containing the main class that create the post data and makes the HTTP
request according to the ATLAS API.
"""

import json
import urllib2
import time
from dateutil import parser
from datetime import datetime

from .version import __version__


class AtlasRequest(object):
    """
    Base class for doing Atlas requests. Contains functions that can be used by
    most Atlas requests.
    """

    url_path = ''

    def __init__(self, **kwargs):
        # build the url.
        self.key = kwargs.get("key", "")
        if "url_path" in kwargs:
            self.url_path = kwargs["url_path"]
        if "server" in kwargs:
            self.server = kwargs["server"]
        else:
            self.server = "atlas.ripe.net"

        self.http_agent = "RIPE ATLAS Cousteau v%s" % __version__

    def build_url(self):
        """
        Builds the request's url combining server, url_path, key
        classes attributes.
        """
        if self.key:
            self.url = "https://%s%s?key=%s" % (
                self.server, self.url_path, self.key
            )
        else:
            self.url = "https://%s%s" % (self.server, self.url_path)

    def post(self):
        """
        Makes the HTTP POST to the url sending post_data.
        """
        self.build_url()
        self._construct_post_data()
        post_data = json.dumps(self.post_data)
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', self.http_agent)
        try:
            response = urllib2.urlopen(req, post_data)
        except urllib2.HTTPError as exc:
            log = {
                "HTTP_MSG": "HTTP ERROR %d: %s" % (exc.code, exc.msg),
                "ADDITIONAL_MSG": exc.read()
            }
            return False, log

        return True, json.load(response)

    def get(self):
        """
        Makes the HTTP GET to the url.
        """
        self.build_url()
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', self.http_agent)
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError as exc:
            log = {
                "HTTP_MSG": "HTTP ERROR %d: %s" % (exc.code, exc.msg),
                "ADDITIONAL_MSG": exc.read()
            }
            return False, log

        return True, json.load(response)


class AtlasCreateRequest(AtlasRequest):
    """
    Class responsible for creating a request for creating a new Atlas
    measurement. Takes as arguments Atlas API key, a list of Atlas measurement
    objects and a list of Atlas sources. Additionally start and end time can be
    specified.
    Usage:
        from ripeatlas import AtlasCreateRequest
        ar = AtlasCreateRequest(**{
            "start_time": start,
            "stop_time": stop,
            "key": "path_to_key",
            "measurements":[measurement1, ...],
            "sources": [source1, ...]
        })
        ar.create()
    """

    url_path = '/api/v1/measurement/'

    def __init__(self, **kwargs):
        super(AtlasCreateRequest, self).__init__(**kwargs)

        self.measurements = kwargs["measurements"]
        self.sources = kwargs["sources"]
        if kwargs.get("start_time"):
            self.start_time = kwargs["start_time"]
        else:
            self.start_time = ""
        if kwargs.get("stop_time"):
            self.stop_time = kwargs["stop_time"]
        else:
            self.stop_time = ""

    def _construct_post_data(self):
        """
        Contructs the data structure that is required from the atlas API based
        on measurements, sources and times user has specified.
        """
        definitions = [msm.build_api_struct() for msm in self.measurements]
        probes = [source.build_api_struct() for source in self.sources]
        self.post_data = {"definitions": definitions, "probes": probes}
        if self.start_time:
            self.post_data.update(
                {"start_time": int(self.start_time.strftime("%s"))}
            )
        if self.stop_time:
            self.post_data.update(
                {"stop_time": int(self.stop_time.strftime("%s"))}
            )

    def create(self):
        """Sends the POST request"""
        return self.post()


class AtlasChangeRequest(AtlasRequest):
    """Atlas request for changing probes for a running measurement.
    post_data = {
        "msm_id": msm,
        "probes": [{
            "action": action,
            "requested": probe_number,
            "type": "probes",
            "value": probe_values
        }]
    }
    """

    url_path = '/api/v1/participation-request/'

    def __init__(self, **kwargs):
        super(AtlasChangeRequest, self).__init__(**kwargs)
        self.msm_id = kwargs["msm_id"]
        self.sources = kwargs["sources"]

    def _construct_post_data(self):
        """
        Contructs the data structure that is required from the atlas API based
        on measurement id, and the sources.
        """
        probes = [source.build_api_struct() for source in self.sources]
        self.post_data = {"msm_id": self.msm_id, "probes": probes}

    def create(self):
        """Sends the POST request"""
        return self.post()


class AtlasStopRequest(AtlasRequest):
    """Atlas request for stopping a measurement."""

    url_path = '/api/v1/measurement/'

    def __init__(self, **kwargs):
        self.msm_id = kwargs["msm_id"]
        self.url_path += "%d/" % self.msm_id
        super(AtlasStopRequest, self).__init__(**kwargs)

    def delete(self):
        """
        Makes the HTTP DELETE to the url.
        """
        self.build_url()
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', self.http_agent)
        req.get_method = lambda: 'DELETE'
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError as exc:
            log = {
                "HTTP_MSG": "HTTP ERROR %d: %s" % (exc.code, exc.msg),
                "ADDITIONAL_MSG": exc.read()
            }
            return False, log

        return True, response

    def create(self):
        """Sends the DELETE request"""
        return self.delete()


class AtlasResultsRequest(AtlasRequest):
    """Atlas request for fetching results of a measurement."""

    url_path = '/api/v1/measurement/%d/result/'

    def __init__(self, **kwargs):
        self.msm_id = kwargs["msm_id"]
        start = kwargs.get("start")
        stop = kwargs.get("stop")
        self.probe_ids = kwargs.get("probe_ids")
        self.clean_start_time(start)
        self.clean_stop_time(stop)
        self.construct_url_path()
        super(AtlasResultsRequest, self).__init__(**kwargs)

    def clean_start_time(self, start):
        """
        Transform start time filter to datetime object if there is any.
        """
        if isinstance(start, datetime):
            self.start = start
        elif isinstance(start, int):
            self.start = datetime.utcfromtimestamp(start)
        elif isinstance(start, str):
            self.start = parser.parse(start)

    def clean_stop_time(self, stop):
        """
        Transform stop time filter to datetime object if there is any.
        """
        if isinstance(stop, datetime):
            self.stop = stop
        elif isinstance(stop, int):
            self.stop = datetime.utcfromtimestamp(stop)
        elif isinstance(stop, str):
            self.stop = parser.parse(stop)

    def construct_url_path(self):
        """
        Construct url path based on base url_path, msm_id and query filters if
        there are any.
        """
        self.url_path = self.url_path % self.msm_id

        if any([self.start, self.stop, self.probe_ids]):
            self.url_path += "?"

        # variable that helps adding '&' in url in case of multiple filters
        filter_exists = False

        if self.start:
            filter_exists = True
            self.url_path += "start=%d" % time.mktime(self.start.timetuple())

        if self.stop:
            filter_exists = True
            if filter_exists:
                self.url_path += "&"
            self.url_path += "stop=%d" % time.mktime(self.stop.timetuple())

        if self.probe_ids:
            if filter_exists:
                self.url_path += "&"
            self.url_path += "prb_id=%s" % ",".join(map(str, self.probe_ids))

    def create(self):
        """Sends the GET request."""
        return self.get()


__all__ = [
    "AtlasStopRequest", "AtlasCreateRequest",
    "AtlasChangeRequest", "AtlasRequest",
    "AtlasResultsRequest"
]
