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
import calendar
from datetime import datetime

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

from .api_meta_data import Probe, Measurement
from .request import AtlasRequest
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

    def __init__(self, return_objects=False, user_agent=None, server=None,
                 verify=True, **filters):
        self._user_agent = user_agent
        self.server = server
        self.verify = verify
        self.api_filters = filters
        self.split_urls = []
        self.total_count_flag = False
        self.current_batch = []
        self._count = []
        self.return_objects = return_objects
        self.atlas_url = self.build_url()

    def build_url(self):
        """Build the url path based on the filter options."""

        if not self.api_filters:
            return self.url

        # Reduce complex objects to simpler strings
        for k, v in self.api_filters.items():
            if isinstance(v, datetime):  # datetime > UNIX timestamp
                self.api_filters[k] = int(calendar.timegm(v.timetuple()))
            if isinstance(v, (tuple, list)):  # tuples & lists > x,y,z
                self.api_filters[k] = ",".join([str(_) for _ in v])

        if (
            self.id_filter in self.api_filters and
            len(str(self.api_filters[self.id_filter])) > self.URL_LENGTH_LIMIT
        ):
            self.build_url_chunks()
            return self.split_urls.pop(0)

        filters = '&'.join("%s=%s" % (k, v) for (k, v) in self.api_filters.items())

        return "%s?%s" % (self.url, filters)

    def build_url_chunks(self):
        """
        If url is too big because of id filter is huge, break id and construct
        several urls to call them in order to abstract this complexity from user.
        """
        CHUNK_SIZE = 500

        id_filter = str(self.api_filters.pop(self.id_filter)).split(',')
        chuncks = list(self.chunks(id_filter, CHUNK_SIZE))
        filters = '&'.join("%s=%s" % (k, v) for (k, v) in self.api_filters.items())

        for chunk in chuncks:
            if filters:
                url = "{0}?{1}&{2}={3}".format(self.url, filters, self.id_filter, ','.join(chunk))
            else:
                url = "{0}?{1}={2}".format(self.url, self.id_filter, ','.join(chunk))
            self.split_urls.append(url)

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
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
            if not self.current_batch:  # Server request gives empty batch, exit
                raise StopIteration()

        current_object = self.current_batch.pop(0)
        if self.return_objects:
            return self.object_class(meta_data=current_object)
        else:
            return current_object

    def next_batch(self):
        """
        Querying API for the next batch of objects and store next url and
        batch of objects.
        """
        is_success, results = AtlasRequest(
            url_path=self.atlas_url,
            user_agent=self._user_agent,
            server=self.server,
            verify=self.verify,
        ).get()

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

    # count attribute to deal with split-up urls and total count
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
        print(probe["id"])
    """
    url = "/api/v2/probes/"
    id_filter = "id__in"
    object_class = Probe


class MeasurementRequest(RequestGenerator):
    """
    Python generator for Measurement meta api.
    e.g.
    for measurement in MeasurementRequest(**{"status": 1}):
        print(measurement["id"])
    """
    url = "/api/v2/measurements/"
    id_filter = "id__in"
    object_class = Measurement


class AnchorRequest(RequestGenerator):
    """
    Python generator for Anchor meta api.
    e.g.
    for anchor in AnchorRequest():
        print(anchor["id"])
    """
    url = "/api/v2/anchors/"
    id_filter = "id__in"
    object_class = None

    def __init__(self, *args, **kwargs):
        super(AnchorRequest, self).__init__(*args, **kwargs)
        self.return_objects = None
