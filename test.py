#!/usr/bin/env python
from datetime import datetime, timedelta
from collections import namedtuple
from ripeatlas.source import AtlasSource
from ripeatlas.request import AtlasRequest
from ripeatlas.measurement import Ping, Traceroute, Dns


def main():
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
    start = datetime.utcnow() + timedelta(minutes=120)
    stop = start + timedelta(minutes=220)
    ar = AtlasRequest(
        **{
            "start_time": start,
            "stop_time": stop,
            #"key": "ea512565-fe81-4930-9519-1e34b0ccf388",
            "key": "ce07b723-c112-4861-889c-3bb7580f1241",
            #"server": "weir-dev.atlas.ripe.net",
            "server": "atlas.ripe.net",
            "measurements": [ping],
            "sources": [source]
        }
    )
    result = namedtuple('Result', 'success response')
    (result.success, result.response) = ar.create()
    print result.success
    print result.response

if __name__ == "__main__":
    main()
