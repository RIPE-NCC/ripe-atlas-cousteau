# Copyright (c) 2016 RIPE NCC
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

"""
Module containing classes responsible for creating different kind of Atlas
measurement objects.
"""


class AtlasMeasurement(object):
    """
    Parent class for creating an Atlas measurement object containing all
    needed options for ATLAS API. The different kind of measurements are
    specified as child classes. These objects can be passed as measurement
    arguments later on when we call AtlasRequest.
    Usage:
        from ripe.atlas.cousteau import Ping
        ping = Ping(**{
            "target": "www.google.gr", "af": 4,
            "description": "testing new wrapper"
        })
    """

    def __init__(self, **kwargs):
        # set to store all options that are used
        self.used_options = set()
        # required options for definitions part
        self.required_options = ["description", "af"]
        self.measurement_type = ""

    def _init(self, **kwargs):
        """
        Initializing required options and set them as attributes as well as
        options coming from user.
        """
        self._init_required_options(**kwargs)
        self.add_option(**kwargs)

    def _store_option(self, option):
        """
        Store option in the used option set. This way we can keep track which
        options user has select to add to instance. This set is used at the
        build_api_struct function when we build the desired data structure from
        user's input.
        """
        self.used_options.add(option)

    def add_option(self, **options):
        """
        Adds an option and its value to the class as an attribute and stores it
        to the used options set.
        """
        for option, value in options.items():
            setattr(self, option, value)
            self._store_option(option)

    def _init_required_options(self, **kwargs):
        """
        Initialize the required option as class members. The value will be
        either None or the specified value in the kwargs or __init__. The logic
        here is to make the required options accesible to edit after a class
        instance has been created.
        """
        for field in self.required_options:
            setattr(self, field, kwargs.get(field))
            self._store_option(field)

    def clean(self):
        """
        Cleans/checks user entered data making sure required options are at
        least present. This might save some queries from being sent if
        they are totally wrong.
        """

        # make sure the correct measurement type is set.
        if not self.measurement_type:
            log = "Please define a valid measurement type."
            raise MalFormattedMeasurement(log)

        # make sure the required fields are set.
        for roption in self.required_options:
            if getattr(self, roption, None) is None:
                log = "%s Measurement field: <%s> is required" % (
                    self.__class__.__name__, roption
                )
                raise MalFormattedMeasurement(log)

    def v2_translator(self, option):
        """
        This is a temporary function that helps move from v1 API to v2 without
        breaking already running script and keep backwards compatibility.
        Translates option name from API v1 to renamed one of v2 API.
        """
        new_option = option
        new_value = getattr(self, option)

        renaming_pairs = {
            "dontfrag": "dont_fragment",
            "maxhops": "max_hops",
            "firsthop": "first_hop",
            "use_NSID": "set_nsid_bit",
            "cd": "set_cd_bit",
            "do": "set_do_bit",
            "qbuf": "include_qbuf",
            "recursion_desired": "set_rd_bit",
            "noabuf": "include_abuf"
        }
        if option in renaming_pairs.keys():
            warninglog = (
                "DeprecationWarning: {0} option has been deprecated and "
                "renamed to {1}."
            ).format(option, renaming_pairs[option])
            print(warninglog)
            new_option = renaming_pairs[option]

        # noabuf was changed to include_abuf so we need a double-negative
        if option == "noabuf":
            new_value = not new_value

        return new_option, new_value

    def build_api_struct(self):
        """
        Calls the clean method of the class and returns the info in a
        structure that Atlas API is accepting.
        """
        self.clean()
        data = {"type": self.measurement_type}

        # add all options
        for option in self.used_options:
            option_key, option_value = self.v2_translator(option)
            data.update({option_key: option_value})

        return data


class Ping(AtlasMeasurement):
    """Class for creating a ping measurement"""

    def __init__(self, **kwargs):
        super(Ping, self).__init__(**kwargs)
        self.measurement_type = "ping"
        self.required_options.extend(["target"])
        self._init(**kwargs)


class Traceroute(AtlasMeasurement):
    """Class for creating a traceroute measurement"""

    def __init__(self, **kwargs):
        super(Traceroute, self).__init__(**kwargs)
        self.measurement_type = "traceroute"
        self.required_options.extend(["target", "protocol"])
        self._init(**kwargs)


class Dns(AtlasMeasurement):
    """Class for creating a DNS measurement"""

    def __init__(self, **kwargs):
        super(Dns, self).__init__(**kwargs)
        self.measurement_type = "dns"
        self.required_options.extend(
            ["query_class", "query_type", "query_argument"]
        )
        self._init(**kwargs)


class Sslcert(AtlasMeasurement):
    """Class for creating an SSL certificate measurement"""

    def __init__(self, **kwargs):
        super(Sslcert, self).__init__(**kwargs)
        self.measurement_type = "sslcert"
        self.required_options.extend(["target"])
        self._init(**kwargs)


class Ntp(AtlasMeasurement):
    """Class for creating an NTP measurement"""

    def __init__(self, **kwargs):
        super(Ntp, self).__init__(**kwargs)
        self.measurement_type = "ntp"
        self.required_options.extend(["target"])
        self._init(**kwargs)


class Http(AtlasMeasurement):
    """Class for creating an HTTP measurement"""

    def __init__(self, **kwargs):
        super(Http, self).__init__(**kwargs)
        self.measurement_type = "http"
        self.required_options.extend(["target"])
        self._init(**kwargs)


class MalFormattedMeasurement(Exception):
    pass

__all__ = ["Ping", "Traceroute", "Dns", "Sslcert", "Ntp", "Http"]
