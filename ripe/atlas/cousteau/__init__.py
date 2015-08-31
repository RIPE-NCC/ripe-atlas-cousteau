from .measurement import Ping, Traceroute, Dns, Sslcert, Ntp
from .source import AtlasSource, AtlasChangeSource
from .request import (
    AtlasRequest,
    AtlasCreateRequest,
    AtlasChangeRequest,
    AtlasStopRequest,
    AtlasResultsRequest
)
from .stream import AtlasStream


class RequestGenerator(object):
    """
    Python generator class that yields results for meta APIs like
    probes/measurements as single objects. It supports any filter APIs support
    in a dummy way, which means it will take accept whatever it passed and
    build url_path from this.
    """

    API_LIMIT = "300"
    url = ""

    def __init__(self, **filters):
        self.api_filters = filters
        self.atlas_url = self.build_url()
        self.current_batch = []
        self.total_count = None

    def build_url(self):
        """Build the url path based on the filter options."""
        basis_url = self.url
        # Add a limit if user hasn't specified one.
        if "limit" not in self.api_filters:
            basis_url = "%s?limit=%s" % (self.url, self.API_LIMIT)

        if not self.api_filters:
            return basis_url

        filters = '&'.join("%s=%s" % (k, v) for (k, v) in self.api_filters.iteritems())

        if "?" in basis_url:
            return "%s&%s" % (basis_url, filters)
        else:
            return "%s?%s" % (basis_url, filters)

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next_batch(self):
        """
        Quering API for the next batch of objects and store next url and
        batch of objects.
        """
        is_success, results = AtlasRequest(**{"url_path": self.atlas_url}).get()
        if is_success:
            if self.total_count is None:
                self.total_count = results["meta"].get("total_count")
            self.atlas_url = results["meta"].get("next")
            self.current_batch = results.get("objects", [])

    def next(self):
        if not self.current_batch:  # If first time or current batch was all given
            if not self.atlas_url:  # We don't have any next url any more, exit
                raise StopIteration()
            self.next_batch()
            if not self.current_batch:  # Server request gaves empty batch, exit
                raise StopIteration()

        return self.current_batch.pop(0)


class ProbeRequest(RequestGenerator):
    """
    Python generator for Probes meta api.
    e.g.
    for probe in ProbeRequest(**{"limit":200, "country_code": "GR"}):
        print probe["id"]
    """
    url = "/api/v1/probe/"


class MeasurementRequest(RequestGenerator):
    """
    Python generator for Measurement meta api.
    e.g.
    for measurement in MeasurementRequest(**{"status": 1}):
        print measurement["msm_id"]
    """
    url = "/api/v1/measurement/"


__all__ = [
    "Ping",
    "Traceroute",
    "Dns",
    "Sslcert",
    "Ntp",
    "AtlasRequest",
    "AtlasChangeRequest",
    "AtlasCreateRequest",
    "AtlasStopRequest",
    "AtlasResultsRequest",
    "AtlasSource",
    "AtlasChangeSource",
    "AtlasStream",
]
