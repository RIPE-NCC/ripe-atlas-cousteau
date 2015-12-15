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

from ripe.atlas.cousteau import (
    AtlasSource,
    AtlasChangeSource
)
from ripe.atlas.cousteau.source import MalFormattedSource
from . import probes_create_schema, probes_change_schema


class TestAtlasSource(unittest.TestCase):

    def test_sane_type_attribute(self):
        """Test sane input for type attribute"""
        for stype in AtlasChangeSource.types_available:
            kwargs = {"requested": 5, "value": "test", "type": stype}
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

    def test_set_tags(self):
        # all ok
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {"include": ["one", "two"], "exclude": ["one", "two"]}}
        source = AtlasSource(**kwargs)
        self.assertEqual(source.clean(), None)
        self.assertEqual(
            source.tags,
            {"include": ["one", "two"], "exclude": ["one", "two"]}
        )
        # include missing
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {"exclude": ["one", "two"]}
        }
        source = AtlasSource(**kwargs)
        self.assertEqual(source.clean(), None)
        # exclude missing
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {"include": ["one", "two"]}
        }
        source = AtlasSource(**kwargs)
        self.assertEqual(source.clean(), None)
        # invalid tag type
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {"include": ["one", 2], "exclude": ["one", "two"]}
        }
        self.assertRaises(MalFormattedSource, lambda: AtlasSource(**kwargs))
        # unknown element
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {
                "include": ["one", 2], "exclude": ["one", "two"], "unknown": "?"
            }
        }
        self.assertRaises(MalFormattedSource, lambda: AtlasSource(**kwargs))

    def test_build_api_struct_with_tags(self):
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {"include": ["one", "two"], "exclude": ["one", "two"]}
        }
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

    def test_set_tags(self):
        # missing action
        kwargs = {
            "requested": 5, "value": "test", "type": "msm",
            "tags": {"include": ["one", "two"], "exclude": ["one", "two"]}
        }
        self.assertRaises(
            MalFormattedSource, lambda: AtlasChangeSource(**kwargs).build_api_struct()
        )
        # action == add
        kwargs = {
            "requested": 5, "value": "test", "type": "msm", "action": "add",
            "tags": {"include": ["one", "two"], "exclude": ["one", "two"]}
        }
        source = AtlasChangeSource(**kwargs)
        self.assertEqual(source.clean(), None)
        # action == remove
        kwargs = {
            "requested": 5, "value": "test", "type": "msm", "action": "remove",
            "tags": {"include": ["one", "two"], "exclude": ["one", "two"]}
        }
        self.assertRaises(
            MalFormattedSource, lambda: AtlasChangeSource(**kwargs)
        )
