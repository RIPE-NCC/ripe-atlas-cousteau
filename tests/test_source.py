import unittest

from ripeatlas.source import (
    AtlasSource,
    AtlasChangeSource,
    MalFormattedSource
)


class TestAtlasSource(unittest.TestCase):

    def setUp(self):
        self.kwargs = {"requested": 5, "value": "test", "type": "country"}
        self.source = AtlasSource(**self.kwargs)

    def test_setting_type(self):
        self.assertRaises(
            MalFormattedSource, lambda: setattr(self.source, "type", "testing")
        )

    def test_clean(self):
        self.assertEqual(self.source.clean(), None)
        self.source.type = "msm"
        self.source.value = None
        self.assertRaises(
            MalFormattedSource, lambda: self.source.clean()
        )
        self.source.value = "test"
        self.source.requested = None
        self.assertRaises(
            MalFormattedSource, lambda: self.source.clean()
        )

    def test_build_api_struct(self):
        self.assertEqual(self.source.build_api_struct(), self.kwargs)


class TestAtlasChangeSource(unittest.TestCase):

    def setUp(self):
        self.kwargs = {
            "requested": 5, "value": "test", "action": "add"
        }
        self.source = AtlasChangeSource(**self.kwargs)

    def test_setting_type(self):
        for source_type in ["area", "country", "prefix", "asn", "msm"]:
            self.assertRaises(
                MalFormattedSource,
                lambda: setattr(self.source, "type", source_type)
            )

        self.assertEqual(setattr(self.source, "type", "probes"), None)

    def test_setting_action(self):
        for source_action in ["remove", "add"]:
            self.assertEqual(
                setattr(self.source, "action", source_action), None
            )

        self.assertRaises(
            MalFormattedSource,
            lambda: setattr(self.source, "action", "test")
        )

    def test_clean(self):
        self.assertEqual(self.source.clean(), None)
        self.source.value = None
        self.assertRaises(
            MalFormattedSource, lambda: self.source.clean()
        )
        self.source.value = "test"
        self.source.requested = None
        self.assertRaises(
            MalFormattedSource, lambda: self.source.clean()
        )

    def test_build_api_struct(self):
        self.kwargs.update({"type": "probes"})
        self.assertEqual(self.source.build_api_struct(), self.kwargs)
