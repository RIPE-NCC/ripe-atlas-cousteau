"""File containing the nose tests"""
from ripe.atlas.cousteau import (
    AtlasSource, AtlasChangeSource, Ping, Traceroute, Dns, Sslcert
)


def test_create_source():
    """Unittest for sources for create request"""
    AtlasSource(**{
        "type": "area", "value": "WW", "requested": 38
    }).build_api_struct()


def test_change_source():
    """Unittest for sources for change request"""
    AtlasChangeSource(**{
        "value": "59", "requested": 1, "action": "remove", "type": "probes"
    }).build_api_struct()
    AtlasChangeSource(**{
        "value": "28", "requested": 1, "action": "add", "type": "area"
    }).build_api_struct()


def test_ping():
    """Unittest for Ping class"""
    Ping(**{
        "target": "www.google.fr",
        "af": 4,
        "description": "testing",
        "prefer_anchors": True
    }).build_api_struct()


def test_dns():
    """Unittest for Dns class"""
    Dns(
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


def test_traceroute():
    """Unittest for Traceroute class"""
    Traceroute(**{
        "af": 4,
        "target": 'www.ripe.net',
        "description": 'testing',
        "protocol": "ICMP",
        "prefer_anchors": True,
    }).build_api_struct()


def test_sslcert():
    """Unittest for Sslcert class"""
    Sslcert(**{
        "af": 4,
        "target": 'www.ripe.net',
        "description": 'testing',
        "prefer_anchors": True,
    }).build_api_struct()
