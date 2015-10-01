"""
Module containing class responsible for creating different Atlas
source objects
"""


class AtlasSource(object):
    """
    Class responsible for creating an Atlas source object that holds
    information about the number of probes, the type of the source and
    the value of the source. This object can be passed as source argument
    later on when we call AtlasRequest.
    Usage:
        from ripe.atlas.cousteau import AtlasSource
        as = AtlasSource(**{"type": "area", "value": "WW", "requested": 5})
    """

    # available types
    types_available = ["area", "country", "prefix", "asn", "probes", "msm"]

    def __init__(self, **kwargs):
        if "requested" in kwargs:
            self.requested = kwargs["requested"]
        else:
            self._requested = None
        if "value" in kwargs:
            self.value = kwargs["value"]
        else:
            self._value = None
        if "type" in kwargs:
            self.type = kwargs["type"]
        else:
            self._type = None

    # requested attribute
    def get_requested(self):
        """Getter for requested attribute"""
        return self._requested

    def set_requested(self, value):
        """Setter for requested attribute"""
        self._requested = value

    doc_req = "Defines how many probes will be requested."
    requested = property(get_requested, set_requested, doc=doc_req)

    # value attribute
    def get_value(self):
        """Getter for value attribute"""
        return self._value

    def set_value(self, value):
        """Setter for value attribute"""
        self._value = value

    doc_value = "Defines the value of the type of probe's source."
    value = property(get_value, set_value, doc=doc_value)

    # type attribute
    def get_type(self):
        """Getter for type attribute"""
        return self._type

    def set_type(self, value):
        """Setter for type attribute"""
        if value not in self.types_available:
            log = "Sources field 'type' should be in one of %s" % (
                self.types_available
            )
            raise MalFormattedSource(log)
        self._type = value

    doc_type = "Defines the type of probe's source."
    type = property(get_type, set_type, doc=doc_type)

    def clean(self):
        """
        Cleans/checks user has entered all required attributes. This might save
        some queries from being sent to server if they are totally wrong.
        """
        if not all([self._requested, self._value, self._type]):
            raise MalFormattedSource(
                "<requested, value, type> fields are required."
            )

    def build_api_struct(self):
        """
        Calls the clean method of the class and returns the info in a structure
        that Atlas API is accepting.
        """
        self.clean()
        return {
            "type": self._type,
            "requested": self._requested,
            "value": self._value
        }


class AtlasChangeSource(AtlasSource):
    """
    Class responsible for creating an Atlas source object for changing
    participants probes for a measurement.
    Usage:
        from ripe.atlas.cousteau import AtlasChangeSource
        as = AtlasChangeSource(**{"type":"area", "value": "WW", "requested": 5})
    """
    def __init__(self, **kwargs):
        if "action" in kwargs:
            self.action = kwargs["action"]
        else:
            self._action = None

        super(AtlasChangeSource, self).__init__(**kwargs)

    # type attribute
    def get_type(self):
        """Getter for type attribute"""
        return self._type

    def set_type(self, value):
        """Setter for type attribute"""
        if self.action == "remove" and value != "probes":
            log = "Sources field 'type' when action is remove should always be 'probes'."
            raise MalFormattedSource(log)
        self._type = value

    doc_type = "Defines the type of probe's source."
    type = property(get_type, set_type, doc=doc_type)

    # action attribute
    def get_action(self):
        """Getter for action attribute"""
        return self._action

    def set_action(self, value):
        """Setter for action attribute"""
        if value not in ("remove", "add"):
            log = "Sources field 'action' should be 'remove' or 'add'."
            raise MalFormattedSource(log)
        self._action = value

    doc_action = "Defines the action (remove/add if the change source)."
    action = property(get_action, set_action, doc=doc_action)

    def clean(self):
        """
        Cleans/checks user has entered all required attributes. This might save
        some queries from being sent to server if they are totally wrong.
        """
        if not all([self._type, self._requested, self._value, self._action]):
            raise MalFormattedSource(
                "<type, requested, value, action> fields are required."
            )

    def build_api_struct(self):
        """
        Calls parent's method and just adds the addtional field 'action', that
        is required to form the structure that Atlas API is accepting.
        """
        data = super(AtlasChangeSource, self).build_api_struct()
        data.update({"action": self._action})
        return data


class MalFormattedSource(Exception):
    """Custom Exception class for malformed sources"""
    pass

__all__ = ["AtlasSource", "AtlasChangeSource"]
