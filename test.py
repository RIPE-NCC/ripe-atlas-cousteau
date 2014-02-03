#!/usr/bin/env python
from datetime import datetime, timedelta
from collections import namedtuple
from ripeatlas.source import AtlasSource, AtlasChangeSource
from ripeatlas.request import AtlasCreateRequest, AtlasChangeRequest
from ripeatlas.measurement import Ping, Traceroute, Dns, Sslcert

def test_create_source():
    """Unittest for sources for create request"""
    AtlasSource(**{"type": "area", "value": "WW", "requested": 38}).build_api_struct()

def test_change_source():
    """Unittest for sources for change request"""
    remove = AtlasChangeSource(**{"value": "59", "requested": 1, "action": "remove"})
    add = AtlasChangeSource(**{"value": "28", "requested": 1, "action": "add", "type": "probes"})

def test_ping():
    """Unittest for Ping class"""
    ping = Ping(**{
        "target": "www.google.fr", 
        "af": 4,
        "description": "testing",
        "prefer_anchors": True
    }).build_api_struct()

def test_dns():
    """Unittest for Dns class"""
    dns = Dns(**{
        "target": "k.root-servers.net", "af": 4,
        "description": "testing new wrapper", "query_type":
        "SOA", "query_class": "IN", "query_argument": "nl",
        "retry": 6
    }).build_api_struct()

def test_traceroute():
    """Unittest for Traceroute class"""
    trace = Traceroute(**{
        "af": 4,
        "target": 'www.ripe.net',
        "description": 'testing'
        "protocol": "ICMP",
        "prefer_anchors": True,
    }).build_api_struct()

def test_sslcert():
    """Unittest for Sslcert class"""
    trace = Sslcert(**{
        "af": 4,
        "target": 'www.ripe.net',
        "description": 'testing'
        "prefer_anchors": True,
    }).build_api_struct()

def test_create_request():
    """Unittest for Atlas create request"""
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
    ar = AtlasCreateRequest(
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
    assert result.success == True

def test_change_request():
    """Unittest for Atlas change request"""
    remove = AtlasChangeSource(**{"value": "59", "requested": 1, "action": "remove"})
    add = AtlasChangeSource(**{"value": "28", "requested": 1, "action": "add", "type": "probes"})
    key = open("api-key", "r").readlines()[0].rstrip('\n')
    server = open("api-server", "r").readlines()[0].rstrip('\n')
    ar = AtlasChangeRequest(
        **{
            "key": key,
            "server": server,
            "msm_id": 1019016,
            "sources": [remove]
        }
    )
    result = namedtuple('Result', 'success response')
    (result.success, result.response) = ar.create()
    assert result.success == True
