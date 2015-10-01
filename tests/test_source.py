import unittest

from jsonschema import validate

from ripe.atlas.cousteau import (
    AtlasSource,
    AtlasChangeSource
)
from ripe.atlas.cousteau.source import MalFormattedSource
from . import probes_create_schema, probes_change_schema


class TestAtlasSource(unittest.TestCase):

    def test_sane_type_attribute(self):
        """Test sane input for type attribute"""
        for t in ("country", "probes", "area", "asn", "prefix"):
            kwargs = {"requested": 5, "value": "test", "type": t}
            AtlasSource(**kwargs)

    def test_wrong_type_attribute(self):
        """Test wrong input for type attribute"""
        kwargs = {"requested": 5, "value": "test", "type": "blaaaaaaa"}
        self.assertRaises(
            MalFormattedSource, lambda: AtlasSource(**kwargs)
        )

    def test_clean(self):
        # all ok
        kwargs = {"requested": 5, "value": "test", "type": "msm"}
        source = AtlasSource(**kwargs)
        self.assertEqual(source.clean(), None)
        # value missing
        source.value = None
        self.assertRaises(
            MalFormattedSource, lambda: source.clean()
        )
        # type missing
        kwargs = {"requested": 5, "value": "test"}
        self.assertRaises(
            MalFormattedSource, lambda: AtlasSource(**kwargs).clean()
        )
        # requested missing
        source.value = "test"
        source.requested = None
        self.assertRaises(
            MalFormattedSource, lambda: source.clean()
        )

    def test_build_api_struct(self):
        kwargs = {"requested": 5, "value": "test", "type": "msm"}
        source = AtlasSource(**kwargs)
        self.assertEqual(source.build_api_struct(), kwargs)
        validate(source.build_api_struct(), probes_create_schema)


class TestAtlasChangeSource(unittest.TestCase):

    def test_setting_type(self):
        kwargs = {
            "requested": 5, "value": "test", "action": "add"
        }
        source = AtlasChangeSource(**kwargs)
        for source_type in ["area", "country", "prefix", "asn", "msm", "probes"]:
            self.assertEqual(setattr(source, "type", source_type), None)

        kwargs = {
            "requested": 5, "value": "test", "action": "remove"
        }
        source = AtlasChangeSource(**kwargs)
        for source_type in ["area", "country", "prefix", "asn", "msm"]:
            self.assertRaises(
                MalFormattedSource,
                lambda: setattr(source, "type", source_type)
            )
        self.assertEqual(setattr(source, "type", "probes"), None)

    def test_setting_action(self):
        kwargs = {
            "requested": 5, "value": "test", "type": "probes"
        }
        source = AtlasChangeSource(**kwargs)
        for source_action in ["remove", "add"]:
            self.assertEqual(
                setattr(source, "action", source_action), None
            )

        self.assertRaises(
            MalFormattedSource,
            lambda: setattr(source, "action", "test")
        )

    def test_clean(self):
        # all ok
        kwargs = {"requested": 5, "value": "test", "type": "msm", "action": "add"}
        source = AtlasChangeSource(**kwargs)
        self.assertEqual(source.clean(), None)
        # value missing
        source.value = None
        self.assertRaises(
            MalFormattedSource, lambda: source.clean()
        )
        # type missing
        kwargs = {"requested": 5, "value": "test", "action": "add"}
        self.assertRaises(
            MalFormattedSource, lambda: AtlasChangeSource(**kwargs).clean()
        )
        # action missing
        kwargs = {"requested": 5, "value": "test", "type": "probes"}
        self.assertRaises(
            MalFormattedSource, lambda: AtlasChangeSource(**kwargs).clean()
        )
        # requested missing
        source.value = "test"
        source.requested = None
        self.assertRaises(
            MalFormattedSource, lambda: source.clean()
        )

    def test_build_api_struct(self):
        kwargs = {"requested": 5, "value": "test", "type": "msm", "action": "add"}
        source = AtlasChangeSource(**kwargs)
        self.assertEqual(source.build_api_struct(), kwargs)
        validate(source.build_api_struct(), probes_change_schema)
