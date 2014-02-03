"""File containing the nose tests"""
#!/usr/bin/env python
from datetime import datetime, timedelta
from nose.exc import SkipTest
from collections import namedtuple
from ripeatlas.source import AtlasSource, AtlasChangeSource
from ripeatlas.request import AtlasCreateRequest, AtlasChangeRequest
from ripeatlas.measurement import Ping, Traceroute, Dns, Sslcert


def test_create_source():
    """Unittest for sources for create request"""
    AtlasSource(**{
        "type": "area", "value": "WW", "requested": 38
    }).build_api_struct()


def test_change_source():
    """Unittest for sources for change request"""
    AtlasChangeSource(**{
        "value": "59", "requested": 1, "action": "remove"
    }).build_api_struct()
    AtlasChangeSource(**{
        "value": "28", "requested": 1, "action": "add", "type": "probes"
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


def test_create_request():
    """Unittest for Atlas create request"""
    raise SkipTest("Skip create request")
    source = AtlasSource(**{"type": "area", "value": "WW", "requested": 38})
    ping = Ping(**{
        "target": "www.google.fr",
        "af": 4,
        "description": "testing",
        "prefer_anchors": True
    })
    dns = Dns(**{
        "target": "k.root-servers.net", "af": 4,
        "description": "testing new wrapper", "query_type": "SOA",
        "query_class": "IN", "query_argument": "nl", "retry": 6
    })
    stop = datetime.utcnow() + timedelta(minutes=220)
    key = open("api-key", "r").readlines()[0].rstrip('\n')
    server = open("api-server", "r").readlines()[0].rstrip('\n')
    request = AtlasCreateRequest(
        **{
            "stop_time": stop,
            "key": key,
            "server": server,
            "measurements": [ping, dns],
            "sources": [source]
        }
    )
    result = namedtuple('Result', 'success response')
    (result.success, result.response) = ar.create()
    assert (result.success)


def test_change_request():
    """Unittest for Atlas change request"""
    raise SkipTest("Skip change request")
    remove = AtlasChangeSource(**{
        "value": "59", "requested": 1, "action": "remove"
    })
    add = AtlasChangeSource(**{
        "value": "28", "requested": 1, "action": "add", "type": "probes"
    })
    key = open("api-key", "r").readlines()[0].rstrip('\n')
    server = open("api-server", "r").readlines()[0].rstrip('\n')
    request = AtlasChangeRequest(
        **{
            "key": key,
            "server": server,
            "msm_id": 1019016,
            "sources": [add, remove]
        }
    )
    result = namedtuple('Result', 'success response')
    (result.success, result.response) = ar.create()
    assert (result.success)
