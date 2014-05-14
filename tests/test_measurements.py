import unittest

from jsonschema import validate

from ripe.atlas.cousteau.measurement import (
    MalFormattedMeasurement,
    AtlasMeasurement
)
from . import definitions_schema


class TestAtlasMeasurement(unittest.TestCase):

    def setUp(self):
        kwargs = {"target": "www.google.gr", "af": 4}
        self.measurement = AtlasMeasurement(**kwargs)
        self.measurement._init(**kwargs)

    def test_add_option(self):
        self.assertRaises(TypeError, lambda: self.measurement.add_option("3"))
        self.assertRaises(TypeError, lambda: self.measurement.add_option(3))
        self.assertRaises(
            TypeError, lambda: self.measurement.add_option(["3"])
        )
        self.assertRaises(
            TypeError, lambda: self.measurement.add_option(*["3"])
        )

        self.measurement.add_option(**{"test": "test"})
        self.assertEqual(self.measurement.test, "test")

    def test_init_required_options(self):
        self.measurement._init_required_options(
            **{"af": 4, "description": "test", "crap": "test"}
        )
        self.assertEqual(self.measurement.af, 4)
        self.assertEqual(self.measurement.description, "test")
        self.assertRaises(
            AttributeError, lambda: getattr(self.measurement, "crap")
        )

    def test_clean(self):
        self.assertRaises(
            MalFormattedMeasurement, lambda: self.measurement.clean()
        )
        self.measurement.measurement_type = "test"
        self.measurement.description = "test"
        self.measurement.clean()

    def test_build_api_struct(self):
        output = {
            "type": "ping",
            "target": "www.google.gr",
            "af": 4,
            "description": "test"
        }
        self.measurement.description = "test"
        self.measurement.measurement_type = "ping"
        self.assertEqual(self.measurement.build_api_struct(), output)
        validate(self.measurement.build_api_struct(), definitions_schema)
