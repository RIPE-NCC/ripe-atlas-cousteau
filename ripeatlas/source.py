"""Module containing class responsible for creating an Atlas source object"""


class AtlasSource(object):
    """
    Class responsible for creating an Atlas source object that holds
    information about the number of probes, the type of the source and
    the value of the source. This object can be passed as source argument
    later on when we call AtlasRequest.
    Usage:
        from ripeatlas import AtlasSource
        as = AtlasSource(**{"type": "area", "value": "WW", "requested": 5})
    """

    # required options for probes part
    required_options = ["requested", "type", "value"]
    required_options_available = {
        "type": ["area", "country", "prefix", "asn", "probes", "msm"]
    }

    def __init__(self, **kwargs):
        for option in self.required_options:
            setattr(self, option, kwargs.get(option))

    def clean(self):
        """
        Cleans/checks user entered data making sure required options are at
        least present. This might save some queries from being sent if
        they are totally wrong.
        """
        for roption in self.required_options:
            if not hasattr(self, roption):
                raise MalFormattedSource(
                    "Sources field: %s is required" % roption
                )
            if (
                roption in self.required_options_available and
                getattr(self, roption) not in self.required_options_available[roption]
            ):
                log = "Sources field: %s should be in one of %s" % (
                    roption,
                    self.required_options_available[roption]
                )
                raise MalFormattedSource(log)

    def build_api_struct(self):
        """
        Calls the clean method of the class and returns the info in a structure
        that Atlas API is accepting.
        """
        self.clean()
        return {
            "type": self.type,
            "requested": self.requested,
            "value": self.value
        }


class MalFormattedSource(Exception):
    pass

__all__ = ["AtlasSource"]
