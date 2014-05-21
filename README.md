# RIPE Atlas Cousteau
[![Build Status](https://travis-ci.org/RIPE-NCC/ripe-atlas-cousteau.png?branch=master)](https://travis-ci.org/RIPE-NCC/ripe-atlas-cousteau) [![Code Health](https://landscape.io/github/RIPE-NCC/ripe-atlas-cousteau/master/landscape.png)](https://landscape.io/github/RIPE-NCC/ripe-atlas-cousteau/master)
A python wrapper around RIPE ATLAS API.

## Installation

You can install by either cloning the repo and run the following inside the repo:

```bash
$ python setup.py install
```

or via pip using:
```bash
$ pip install https://github.com/RIPE-NCC/ripe-atlas-cousteau/zipball/master
```

## Usage
Creating two new RIPE Atlas UDMs is as easy as:
```python
from ripe.atlas.cousteau import (
    Ping, 
    Traceroute,
    AtlasSource, 
    AtlasCreateRequest
)

ATLAS_API_KEY = ""

ping = Ping(**{
    "af": 4,
    "target": "www.google.gr",
    "description": "testing new wrapper"
})

traceroute = Traceroute(**{
    "af": 4,
    "target": 'www.ripe.net',
    "description": 'testing',
    "protocol": "ICMP",
})

source = AtlasSource(**{
    "type": "area",
    "value": "WW",
    "requested": 5 
})

atlas_request = AtlasCreateRequest(**{
    "start_time": datetime.utcnow(),
    "key": ATLAS_API_KEY,
    "measurements": [ping, traceroute],
    "sources": [source]
})

(is_success, response) = atlas_request.create()
```

Similarly if you want to change probes for an existing measurement you can do:
```python
from ripe.atlas.cousteau import (
    AtlasChangeSource, 
    AtlasChangeRequest
)

ATLAS_MODIFY_API_KEY = ""

source = AtlasChangeSource(**{
    "value": "1,2,3",
    "requested": 3,
    "action": "remove"
})

atlas_request = AtlasChangeRequest(**{
    "key": ATLAS_MODIFY_API_KEY,
    "msm_id": 1000001,
    "sources": [source]
})

(is_success, response) = atlas_request.create()
```
Same applies if you want to add a list of probes, you just have to change "action" key to "add" as stated on the [docs](https://atlas.ripe.net/docs/rest/#participation-request).
Or stopping a measurement:
```python
from ripe.atlas.cousteau import AtlasStopRequest

ATLAS_STOP_API_KEY = ""

atlas_request = AtlasStopRequest(**{
"msm_id": 1000001,
"key": ATLAS_STOP_API_KEY,
})

(is_success, response) = atlas_request.create()
```

In order to be able to successfully create most of the above you need to create an [API key](https://atlas.ripe.net/docs/keys/).
Also keep in mind that this library is trying to comply with what is stated in the [documentation pages](https://atlas.ripe.net/docs/measurement-creation-api/). This means that if you try to create a request that is missing a field stated as required, the library won't go ahead and do the HTTP query. On the contrary, it will raise an exception with some info in it.

## Colophon

But why [Cousteau](http://en.wikipedia.org/wiki/Jacques_Cousteau)? The RIPE Atlas team decided to name all of its modules after explorers, and this is not an exception :)
