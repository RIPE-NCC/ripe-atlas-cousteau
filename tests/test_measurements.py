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
