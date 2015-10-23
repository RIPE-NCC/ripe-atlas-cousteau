"""File containing the nose tests"""
import unittest

from ripe.atlas.cousteau import (
    Ping, Traceroute, Dns, Sslcert, Ntp, Http
)


class TestMeasurementTypes(unittest.TestCase):

    def test_ping(self):
        """Unittest for Ping class"""
        post_body = Ping(**{
            "target": "www.google.fr",
            "af": 4,
            "description": "testing",
            "prefer_anchors": True
        }).build_api_struct()
        expected_output = {
            'description': 'testing', 'af': 4, 'type': 'ping',
            'target': 'www.google.fr', 'prefer_anchors': True
        }
        self.assertEqual(post_body, expected_output)

    def test_dns(self):
        """Unittest for Dns class"""
        post_body = Dns(
            **{
                "target": "k.root-servers.net",
                "af": 4,
                "description": "testing",
                "query_type": "SOA",
                "query_class": "IN",
                "query_argument": "nl",
                "retry": 6
            }
        ).build_api_struct()
        expected_output = {
            'query_class': 'IN', 'retry': 6, 'description': 'testing', 'af': 4,
            'query_argument': 'nl', 'query_type': 'SOA', 'type': 'dns',
            'target': 'k.root-servers.net'
        }
        self.assertEqual(post_body, expected_output)

    def test_traceroute(self):
        """Unittest for Traceroute class"""
        post_body = Traceroute(**{
            "af": 4,
            "target": 'www.ripe.net',
            "description": 'testing',
            "protocol": "ICMP",
            "prefer_anchors": True,
        }).build_api_struct()
        expected_output = {
            'protocol': 'ICMP', 'description': 'testing', 'prefer_anchors': True,
            'af': 4, 'type': 'traceroute', 'target': 'www.ripe.net'
        }
        self.assertEqual(post_body, expected_output)

    def test_sslcert(self):
        """Unittest for Sslcert class"""
        post_body = Sslcert(**{
            "af": 4,
            "target": 'www.ripe.net',
            "description": 'testing',
            "prefer_anchors": True,
        }).build_api_struct()
        expected_output = {
            'description': 'testing', 'af': 4, 'type': 'sslcert',
            'target': 'www.ripe.net', 'prefer_anchors': True
        }
        self.assertEqual(post_body, expected_output)

    def test_ntpcert(self):
        """Unittest for Ntp class"""
        post_body = Ntp(**{
            "af": 4,
            "target": 'www.ripe.net',
            "description": 'testing',
            "prefer_anchors": True,
        }).build_api_struct()
        expected_output = {
            'description': 'testing', 'af': 4, 'type': 'ntp',
            'target': 'www.ripe.net', 'prefer_anchors': True
        }
        self.assertEqual(post_body, expected_output)

    def test_http(self):
        """Unittest for HTTP class"""
        post_body = Http(**{
            "af": 4,
            "target": 'www.ripe.net',
            "description": 'testing',
            "prefer_anchors": True,
        }).build_api_struct()
        expected_output = {
            'description': 'testing', 'af': 4, 'type': 'http',
            'target': 'www.ripe.net', 'prefer_anchors': True
        }
        self.assertEqual(post_body, expected_output)
