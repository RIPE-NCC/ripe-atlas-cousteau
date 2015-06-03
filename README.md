# RIPE Atlas Cousteau

A python wrapper around RIPE ATLAS API.

[![Build Status](https://travis-ci.org/RIPE-NCC/ripe-atlas-cousteau.png?branch=master)](https://travis-ci.org/RIPE-NCC/ripe-atlas-cousteau) [![Code Health](https://landscape.io/github/RIPE-NCC/ripe-atlas-cousteau/master/landscape.png)](https://landscape.io/github/RIPE-NCC/ripe-atlas-cousteau/master)

## Installation

You can install by either cloning the repo and run the following inside the repo:

```bash
$ python setup.py install
```

or via pip using:
```bash
$ pip install https://github.com/RIPE-NCC/ripe-atlas-cousteau/zipball/latest
```

## Usage
### Measurement Creation
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
Keep in mind that this library is trying to comply with what is stated in the [documentation pages](https://atlas.ripe.net/docs/measurement-creation-api/). This means that if you try to create a request that is missing a field stated as required, the library won't go ahead and do the HTTP query. On the contrary, it will raise an exception with some info in it.
### Changing Measurement Sources
Similarly if you want to change (remove in the following example) probes for an existing measurement you can do:
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
### Stop Measurement
You can stop a measurement with:
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

### Make Any API Get Requests
If you know the url path you can make any request easily towards ATLAS API.
```
msm_id = 2016892
url_path = (
    "api/v1/measurement/{0}/?fields=participant_count&"
    "format=json"
).format(msm_id)
request = AtlasRequest(**{
    "url_path": url_path
})
result = namedtuple('Result', 'success response')
(is_success, response) = request.get()
if not is_success:
    return False

return result.response["participant_count"]
```
### Fetch Results
You can fetch results for any measurements using cousteau. In the following example we are getting all results for measurement ID 2016892 and for probe IDs 1,2,3,4 between 2015-05-19 and 2015-05-20. Times can be python datetime objects, Unix timestamps or string representations of dates.
```
from ripe.atlas.cousteau import AtlasResultsRequest

kwargs = {
    "msm_id": 2016892,
    "start": datetime(2015, 05, 19)
    "stop": datetime(2015, 05, 20)
    "probe_ids": [1,2,3,4]
}
is_success, results = AtlasResultsRequest(**kwargs).create()
if is_success:
    print results
```
### Fetch Probes/Measurements Meta data
This is a helpful feature that hides all the complexity of traversing the API using the next url each time there are more objects. It returns a python generator that you can use to access each object.

Fetches all probes from NL with asn_v4 3333 and with tag NAT
```
from ripe.atlas.cousteau import ProbeRequest

filters = {"tags": "NAT", "country_code": "NL", "asn_v4": "3333"}
probes = ProbeRequest(**filters)

for probe in probes:
    print probe["id"]

# Print total count of found probes
print probes.total_count
```
Fetches all specified measurements.
```
from ripe.atlas.cousteau import MeasurementRequest

filters = {"status": 1}
measurements = MeasurementRequest(**filters)

for msm in measurements:
    print msm["msm_id"]

# Print total count of found measurements
print measurements.total_count
```
## Colophon

But why [Cousteau](http://en.wikipedia.org/wiki/Jacques_Cousteau)? The RIPE Atlas team decided to name all of its modules after explorers, and this is not an exception :)
