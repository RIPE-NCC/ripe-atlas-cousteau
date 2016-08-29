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
from datetime import datetime
from dateutil.tz import tzutc

from .request import AtlasRequest
from .exceptions import CousteauGenericError, APIResponseError


class EntityRepresentation(object):
    """
    A crude representation of entity's meta data as we get it from the API.
    """

    API_META_URL = ""

    def __init__(self, **kwargs):

        self.id = kwargs.get("id")
        self.server = kwargs.get("server")
        self.verify = kwargs.get("verify", True)
        self.api_key = kwargs.get("key", "")
        self.meta_data = kwargs.get("meta_data")
        self._user_agent = kwargs.get("user_agent")
        self._fields = kwargs.get("fields")
        self.get_params = {}

        if self.meta_data is None and self.id is None:
            raise CousteauGenericError(
                "Id or meta_data should be passed in order to create object."
            )

        if self._fields:
            self.update_get_params()

        if self.meta_data is None:
            if not self._fetch_meta_data():
                raise APIResponseError(self.meta_data)

        self._populate_data()

    def update_get_params(self):
        """Update HTTP GET params with the given fields that user wants to fetch."""
        if isinstance(self._fields, (tuple, list)):  # tuples & lists > x,y,z
            self.get_params["fields"] = ",".join([str(_) for _ in self._fields])
        elif isinstance(self._fields, str):
            self.get_params["fields"] = self._fields

    def _fetch_meta_data(self):
        """Makes an API call to fetch meta data for the given probe and stores the raw data."""
        is_success, meta_data = AtlasRequest(
            url_path=self.API_META_URL.format(self.id),
            key=self.api_key,
            server=self.server,
            verify=self.verify,
            user_agent=self._user_agent
        ).get(**self.get_params)

        self.meta_data = meta_data
        if not is_success:
            return False

        return True

    def _populate_data(self):
        """
        Passing some raw meta data from API response to instance properties
        """
        raise NotImplementedError()


class Probe(EntityRepresentation):
    """
    A crude representation of probe's meta data as we get it from the API.
    """
    API_META_URL = "/api/v2/probes/{0}/"

    def _populate_data(self):
        """Assing some probe's raw meta data from API response to instance properties"""
        if self.id is None:
            self.id = self.meta_data.get("id")
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
        self.geometry = self.meta_data.get("geometry")
        self.tags = self.meta_data.get("tags")
        self.status = self.meta_data.get("status", {}).get("name")

    def __str__(self):
        return "Probe #{0}".format(self.id)

    def __repr__(self):
        return str(self)


class Measurement(EntityRepresentation):
    """
    A crude representation of measurement's meta data as we get it from the API.
    """
    API_META_URL = "/api/v2/measurements/{0}/"

    def _populate_data(self):
        """Assinging some measurement's raw meta data from API response to instance properties"""
        if self.id is None:
            self.id = self.meta_data.get("id")

        self.stop_time = None
        self.creation_time = None
        self.start_time = None
        self.populate_times()
        self.protocol = self.meta_data.get("af")
        self.target_ip = self.meta_data.get("target_ip")
        self.target_asn = self.meta_data.get("target_asn")
        self.target = self.meta_data.get("target")
        self.description = self.meta_data.get("description")
        self.is_oneoff = self.meta_data.get("is_oneoff")
        self.is_public = self.meta_data.get("is_public")
        self.interval = self.meta_data.get("interval")
        self.resolve_on_probe = self.meta_data.get("resolve_on_probe")
        self.status_id = self.meta_data.get("status", {}).get("id")
        self.status = self.meta_data.get("status", {}).get("name")
        self.type = self.get_type()
        self.result_url = self.meta_data.get("result")

    def get_type(self):
        """
        Getting type of measurement keeping backwards compatibility for
        v2 API output changes.
        """
        mtype = None
        if "type" not in self.meta_data:
            return mtype

        mtype = self.meta_data["type"]
        if isinstance(mtype, dict):
            mtype = self.meta_data.get("type", {}).get("name", "").upper()
        elif isinstance(mtype, str):
            mtype = mtype

        return mtype

    def populate_times(self):
        """
        Populates all different meta data times that comes with measurement if
        they are present.
        """
        stop_time = self.meta_data.get("stop_time")
        if stop_time:
            stop_naive = datetime.utcfromtimestamp(stop_time)
            self.stop_time = stop_naive.replace(tzinfo=tzutc())

        creation_time = self.meta_data.get("creation_time")
        if creation_time:
            creation_naive = datetime.utcfromtimestamp(creation_time)
            self.creation_time = creation_naive.replace(tzinfo=tzutc())

        start_time = self.meta_data.get("start_time")
        if start_time:
            start_naive = datetime.utcfromtimestamp(start_time)
            self.start_time = start_naive.replace(tzinfo=tzutc())

    def __str__(self):
        return "Measurement #{0}".format(self.id)

    def __repr__(self):
        return str(self)
