"""
Module containing the main class that create the post data and makes the HTTP
request according to the ATLAS API.
"""

import json
import urllib2


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
            server = kwargs["server"]
        else:
            server = "atlas.ripe.net"
        if self.key:
            self.url = "https://%s%s?key=%s" % (
                server, self.url_path, self.key
            )
        else:
            self.url = "https://%s%s" % (server, self.url_path)

    def post(self):
        """
        Makes the HTTP POST to the url sending post_data.
        """
        self._construct_post_data()
        post_data = json.dumps(self.post_data)
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
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
        print self.url
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
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
    """Atlas reuest for changing probes for a running measurement.
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

__all__ = ["AtlasCreateRequest", "AtlasChangeRequest", "AtlasRequest"]
