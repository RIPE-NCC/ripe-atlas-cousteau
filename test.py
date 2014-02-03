#!/usr/bin/env python
from datetime import datetime, timedelta
from collections import namedtuple
from ripeatlas.source import AtlasSource, AtlasChangeSource
from ripeatlas.request import AtlasCreateRequest, AtlasChangeRequest
from ripeatlas.measurement import Ping, Traceroute, Dns


def main():
    #source = AtlasSource(**{"type": "area", "value": "WW", "requested": 38})
    #ping = Ping(**{
    #    "target": "www.google.fr", 
    #    "af": 4,
    #    "description": "testing",
    #    "prefer_anchors": True
    #})
    #dns = Dns(**{
    #    "target": "k.root-servers.net", "af": 4,
    #    "description": "testing new wrapper", "query_type": "SOA",
    #    "query_class": "IN", "query_argument": "nl", "retry": 6
    #})
    #start = datetime.utcnow() + timedelta(minutes=120)
    #stop = start + timedelta(minutes=220)
    #key = open("api-key", "r").readlines()[0].rstrip('\n')
    #server = open("api-server", "r").readlines()[0].rstrip('\n')
    #ar = AtlasCreateRequest(
    #    **{
    #        "start_time": start,
    #        "stop_time": stop,
    #        "key": key,
    #        "server": server,
    #        "measurements": [ping],
    #        "sources": [source]
    #    }
    #)
    #result = namedtuple('Result', 'success response')
    #(result.success, result.response) = ar.create()
    #print result.success
    #print result.response
    remove = AtlasChangeSource(**{"value": "69", "requested": 1, "action": "remove"})
    add = AtlasChangeSource(**{"value": "95", "requested": 1, "action": "add", "type": "probes"})
    key = open("api-key", "r").readlines()[0].rstrip('\n')
    server = open("api-server", "r").readlines()[0].rstrip('\n')
    ar = AtlasChangeRequest(
        **{
            "key": key,
            "server": server,
            "msm_id": 1019016,
            "sources": [add, remove]
        }
    )
    result = namedtuple('Result', 'success response')
    print ar.url
    ar._construct_post_data()
    print ar.post_data
    (result.success, result.response) = ar.create()
    print result.success
    print result.response

if __name__ == "__main__":
    main()
