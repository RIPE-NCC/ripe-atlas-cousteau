"""
Module containing the main class that create the post data and makes the HTTP
request according to the ATLAS API.
"""

import json
import urllib2


class AtlasRequest(object):
    """
    Class responsible for creating post data and doing the post query.
    Takes as arguments Atlas API key, a list of Atlas measurement objects and a
    list of Atlas sources. Additionally start and end time can be specified.
    Usage:
        from ripeatlas import AtlasRequest
        ar = AtlasRequest(**{
            "start_time": start,
            "stop_time": stop,
            "key": "path_to_key",
            "measurements":[measurement1, ...],
            "sources": [source1, ...]
        })
        ar.create()
    """

    def __init__(self, **kwargs):
        # build the post url.
        url_path = '/api/v1/measurement/?key='
        self.key = kwargs["key"]
        if "server" in kwargs:
            self.url = "https://%s%s%s" % (kwargs["server"], url_path, self.key)
        else:
            self.url = "https://atlas.ripe.net%s%s" % (url_path, self.key)

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
        """
        Makes the http post that create the UDM(s).
        """
        self._construct_post_data()
        post_data = json.dumps(self.post_data)
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        try:
            response = urllib2.urlopen(req, post_data)
        except urllib2.HTTPError as e:
            log = {
                "HTTP_MSG": "HTTP ERROR %d: %s" % (e.code, e.msg), 
                "ADDITIONAL_MSG": e.read()
            }
            return False, log

        return True, json.load(response)

__all__ = ["AtlasRequest"]
