try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse
from datetime import datetime

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
from .exceptions import APIResponseError


class RequestGenerator(object):
    """
    Python generator class that yields results for meta APIs like
    probes/measurements as single objects. It supports any filter APIs support
    in a dummy way, which means it will take accept whatever it passed and
    build url_path from this.
    """

    url = ""
    id_filter = ""
    URL_LENGTH_LIMIT = 5000

    def __init__(self, **filters):
        self.api_filters = filters
        self.split_urls = []
        self.total_count_flag = False
        self.current_batch = []
        self._count = []
        self.atlas_url = self.build_url()

    def build_url(self):
        """Build the url path based on the filter options."""

        if not self.api_filters:
            return self.url

        if (
            self.id_filter in self.api_filters and
            len(str(self.api_filters[self.id_filter])) > self.URL_LENGTH_LIMIT
        ):
            self.build_url_chunks()
            return self.split_urls.pop(0)

        filters = '&'.join("%s=%s" % (k, v) for (k, v) in self.api_filters.iteritems())

        return "%s?%s" % (self.url, filters)

    def build_url_chunks(self):
        """
        If url is too big because of id filter is huge, break id and construct
        several urls to call them in order to abstract this complexity from user.
        """
        CHUNK_SIZE = 500

        id_filter = str(self.api_filters.pop(self.id_filter)).split(',')
        chuncks = list(self.chunks(id_filter, CHUNK_SIZE))
        filters = '&'.join("%s=%s" % (k, v) for (k, v) in self.api_filters.iteritems())

        for chunk in chuncks:
            if filters:
                url = "{0}?{1}&{2}={3}".format(self.url, filters, self.id_filter, ','.join(chunk))
            else:
                url = "{0}?{1}={2}".format(self.url, self.id_filter, ','.join(chunk))
            self.split_urls.append(url)

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if not self.current_batch:  # If first time or current batch was all given
            if not self.atlas_url:  # We don't have any next url any more, exit
                raise StopIteration()
            self.next_batch()
            if not self.current_batch:  # Server request gaves empty batch, exit
                raise StopIteration()

        return self.current_batch.pop(0)

    def next_batch(self):
        """
        Quering API for the next batch of objects and store next url and
        batch of objects.
        """
        is_success, results = AtlasRequest(**{"url_path": self.atlas_url}).get()

        if not is_success:
            raise APIResponseError(results)

        self.total_count = results.get("count")
        self.atlas_url = self.build_next_url(results.get("next"))
        self.current_batch = results.get("results", [])

    def build_next_url(self, url):
        """Builds next url in a format compatible with cousteau. Path + query"""
        if not url:
            if self.split_urls:  # If we had a long request give the next part
                self.total_count_flag = False  # Reset flag for count
                return self.split_urls.pop(0)
            else:
                return None

        parsed_url = urlparse(url)
        return "{0}?{1}".format(parsed_url.path, parsed_url.query)

    # count attribute to deal with splitted urls and total count
    def get_total_count(self):
        """Getter for count attribute"""
        if not self._count:
            return 0
        else:
            return sum(self._count)

    def set_total_count(self, value):
        """Setter for count attribute. Set should append only one count per splitted url."""
        if not self.total_count_flag and value:
            self._count.append(int(value))
            self.total_count_flag = True

    doc_count = "Defines how many objects returned."
    total_count = property(get_total_count, set_total_count, doc=doc_count)


class ProbeRequest(RequestGenerator):
    """
    Python generator for Probes meta api.
    e.g.
    for probe in ProbeRequest(**{"limit":200, "country_code": "GR"}):
        print probe["id"]
    """
    url = "/api/v2/probes/"
    id_filter = "id__in"


class MeasurementRequest(RequestGenerator):
    """
    Python generator for Measurement meta api.
    e.g.
    for measurement in MeasurementRequest(**{"status": 1}):
        print measurement["msm_id"]
    """
    url = "/api/v2/measurements/"
    id_filter = "msm_id__in"


class EntityRepresentation(object):
    """
    A crude representation of entity's meta data as we get it from the API.
    """

    API_META_URL = "/api/v1/probe/{0}/"

    def __init__(self, **kwargs):

        self.id = kwargs.get("id")
        self.api_key = kwargs.get("key", "")
        self.meta_data = None
        if not self._fetch_meta_data():
            raise APIResponseError(self.meta_data)
        self._populate_data()

    def _fetch_meta_data(self):
        """Makes an API call to fetch meta data for the given probe and stores the raw data."""
        is_success, meta_data = AtlasRequest(
            **{"url_path": self.API_META_URL.format(self.id), "key": self.api_key}
        ).get()

        self.meta_data = meta_data
        if not is_success:
            return False

        return True

    def _populate_data(self):
        """Assing some raw meta data from API response to instance properties"""
        raise NotImplementedError()

    def __str__(self):
        return "Probe #{}".format(self.id)

    def __repr__(self):
        return str(self)


class Probe(EntityRepresentation):
    """
    A crude representation of probe's meta data as we get it from the API.
    """
    API_META_URL = "/api/v1/probe/{0}/"

    def _populate_data(self):
        """Assing some probe's raw meta data from API response to instance properties"""
        self.is_anchor = self.meta_data.get("is_anchor")
        self.country_code = self.meta_data.get("country_code")
        self.description = self.meta_data.get("description")
        self.is_public = self.meta_data.get("is_public")
        self.asn_v4 = self.meta_data.get("asn_v4")
        self.asn_v6 = self.meta_data.get("asn_v6")
        self.address_v4 = self.meta_data.get("address_v4")
        self.address_v6 = self.meta_data.get("address_v6")
        self.prefix_v4 = self.meta_data.get("prefix_v4")
        self.prefix_v6 = self.meta_data.get("prefix_v6")
        self.geometry = (self.meta_data.get("latitude"), self.meta_data.get("longitude"))
        self.status = self.meta_data.get("status_name")


class Measurement(EntityRepresentation):
    """
    A crude representation of measurement's meta data as we get it from the API.
    """
    API_META_URL = "/api/v1/measurement/{0}/"

    def _populate_data(self):
        """Assing some measurement's raw meta data from API response to instance properties"""
        self.protocol = self.meta_data.get("af")
        self.destination_address = self.meta_data.get("dst_addr")
        self.destination_asn = self.meta_data.get("dst_asn")
        self.destination_name = self.meta_data.get("dst_name")
        self.description = self.meta_data.get("description")
        self.is_oneoff = self.meta_data.get("is_oneoff")
        self.is_public = self.meta_data.get("is_public")
        self.interval = self.meta_data.get("interval")
        self.resolve_on_probe = self.meta_data.get("resolve_on_probe")
        self.creation_time = datetime.fromtimestamp(self.meta_data.get("creation_time"))
        self.start_time = datetime.fromtimestamp(self.meta_data.get("start_time"))
        self.stop_time = datetime.fromtimestamp(self.meta_data.get("stop_time"))
        self.status = self.meta_data.get("status", {}).get("name")
        self.type = self.meta_data.get("type", {}).get("name").upper()
        self.result_url = self.meta_data.get("result")

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
