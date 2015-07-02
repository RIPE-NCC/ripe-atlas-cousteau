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

    def build_api_struct(self):
        """
        Calls the clean method of the class and returns the info in a
        structure that Atlas API is accepting.
        """
        self.clean()
        data = {"type": self.measurement_type}

        # add all options
        for option in self.used_options:
            data.update({option: getattr(self, option)})

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


class MalFormattedMeasurement(Exception):
    pass

__all__ = ["Ping", "Traceroute", "Dns", "Sslcert"]
