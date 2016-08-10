.. _use-and-examples:

Use & Examples
**************

This wrapper is using RIPE Atlas v2 API. It covers majority of API calls but not all of them. For some of these calls you will need to have a specific API key tyhat you can get from here.

Creating Measurements
=====================

.. important::
   An `API key`_ is needed with "create a new measurement" permission.

You can create multiple measurements with one API request that will share though same start/end time and allocated probes. This means that if you create a ping and a traceroute with one call they will start and finish at the same time and will use same probes.

Measurement Types
-----------------

The first step is to create the measurement specification object. Currently you can use the following measurement types objects:

- Ping
- Traceroute
- Dns
- Sslcert
- Ntp
- Http

You can initialise any of these objects by passing any of arguments stated in the `documentation pages`_. Keep in mind that this library is trying to comply with what is stated
in these docs. This means that if you try to create a
measurement that is missing a field stated as required in these docs, the library won't go
ahead and do the HTTP query. On the contrary, it will raise an exception
with some info in it.
The required fields for each of the above type are:

+-------------+-------------+----------------+-------------+-------------+-------------+
|     Ping    |  Traceroute |       Dns      |   Sslcert   |     Ntp     |     Http    |
+=============+=============+================+=============+=============+=============+
|      af     |      af     |       af       |      af     |      af     |      af     |
+-------------+-------------+----------------+-------------+-------------+-------------+
| description | description |   description  | description | description | description |
+-------------+-------------+----------------+-------------+-------------+-------------+
|    target   |    target   |   query_class  |    target   |    target   |    target   |
+-------------+-------------+----------------+-------------+-------------+-------------+
|             |   protocol  |   query_type   |             |             |             |
+-------------+-------------+----------------+-------------+-------------+-------------+
|             |             | query_argument |             |             |             |
+-------------+-------------+----------------+-------------+-------------+-------------+

Examples:

.. code:: python

    from ripe.atlas.cousteau import (
      Ping,
      Traceroute
    )

    ping = Ping(
        af=4,
        target="www.google.gr",
        description="Ping Test"
    )

    traceroute = Traceroute(
        af=4,
        target="www.ripe.net",
        description="Traceroute Test",
        protocol="ICMP",
    )

Measurement Sources
-------------------
The second step is to create the measurements source(s). In order to do that you have to create an AtlasSource object using the arguments type, value, requested, and optionally tags.
Type as described in the `documentation pages`_ should be one of the "area", "country", "prefix", "asn", "probes", "msm". Value is the actual value of the type and requested is the number of probes that will be selected from this source.
Optionally you can use tags argument, which has to be a dictionary like {"include": [], "exclude": []}.
Examples:

.. code:: python

    from ripe.atlas.cousteau import AtlasSource

    source = AtlasSource(
        type="area",
        value="WW",
        requested=5,
        tags={"include":["system-ipv4-works"]}
    )
    source1 = AtlasSource(
        type="country",
        value="NL",
        requested=50,
        tags={"exclude": ["system-anchor"]}
    )

Create Request
--------------
The last step is to make the actual HTTP request. Before you do this you need at least to specify if you measurements will be oneoff and you API key.
Additional you can have start and stop time defined.

Examples:

.. code:: python

    from datetime import datetime
    from ripe.atlas.cousteau import (
      Ping,
      Traceroute,
      AtlasSource,
      AtlasCreateRequest
    )

    ATLAS_API_KEY = ""

    ping = Ping(af=4, target="www.google.gr", description="testing new wrapper")

    traceroute = Traceroute(
        af=4,
        target="www.ripe.net",
        description="testing",
        protocol="ICMP",
    )

    source = AtlasSource(
        type="area",
        value="WW",
        requested=5,
        tags={"include":["system-ipv4-works"]}
    )
    source1 = AtlasSource(
        type="country",
        value="NL",
        requested=50,
        tags={"exclude": ["system-anchor"]}
    )


    atlas_request = AtlasCreateRequest(
        start_time=datetime.utcnow(),
        key=ATLAS_API_KEY,
        measurements=[ping, traceroute],
        sources=[source, source1],
        is_oneoff=True
    )

    (is_success, response) = atlas_request.create()


Changing Measurement Sources
============================

.. important::
   An `API key`_ is needed with "change parameters of a measurement" permission.

If you want to add or remove probes from an existing measurement you have to use the AtlasChangeRequest.
First step is to create an AtlasChangeSource objects which is similar to AtlasSource object for the creation of measurements.
The difference is that here you have to specify an additional action argument. This parameter takes only two values "add" or "remove".
In case of "remove" the type of the source can only be "probes". For more info check the appropriate `docs`_.

Example:

.. code:: python

    from ripe.atlas.cousteau import AtlasChangeSource, AtlasChangeRequest

    ATLAS_MODIFY_API_KEY = ""

    # Add probes
    source = AtlasChangeSource(
        value="GR",
        requested=3,
        type="country",
        tags={"include":["system-ipv4-works"], "exclude": ["system-anchor"]},
        action="add"
    )
    source1 = AtlasChangeSource(
        value="4,5,6",
        requested=3,
        type="probes",
        action="add"
    )

    # Remove probes
    source2 = AtlasChangeSource(
        value="1,2,3",
        type="probes",
        requested=3,
        action="remove"
    )

    atlas_request = AtlasChangeRequest(
        key=ATLAS_MODIFY_API_KEY,
        msm_id=1000001,
        sources=[source, source1, source2]
    )

    (is_success, response) = atlas_request.create()


Stopping Measurement
====================

.. important::
  An `API key`_ is needed with "stop a measurement" permission.

You can stop a measurement by creating a AtlasStopRequest and specifying measurement ID as shown below:

.. code:: python

    from ripe.atlas.cousteau import AtlasStopRequest

    ATLAS_STOP_API_KEY = ""

    atlas_request = AtlasStopRequest(msm_id=1000001, key=ATLAS_STOP_API_KEY)

    (is_success, response) = atlas_request.create()


Results
=======
Fetching Results
----------------
.. note::
  If measurement is not public you will need an `API key`_  with "download results of a measurement" permission.

You can fetch results for any measurements using AtlasResultsRequest. You can filter them by start/end time and probes.
Times can be python datetime objects, Unix timestamps or string representations of dates.

Example:

.. code:: python

    from datetime import datetime
    from ripe.atlas.cousteau import AtlasResultsRequest

    kwargs = {
        "msm_id": 2016892,
        "start": datetime(2015, 05, 19),
        "stop": datetime(2015, 05, 20),
        "probe_ids": [1,2,3,4]
    }

    is_success, results = AtlasResultsRequest(**kwargs).create()

    if is_success:
        print(results)


Fetching Latest Results
-----------------------
.. note::
  If measurement is not public you will need an `API key`_  with "download results of a measurement" permission.

In case you want to download latest results of a measurement or your measurement is an oneoff measurements is easier and faster to use the API for the latest results.
Fetching latest results is done by using AtlasLatestRequest and there is an option for filtering by probes.

Example:

.. code:: python

    from ripe.atlas.cousteau import AtlasLatestRequest

    kwargs = {
        "msm_id": 2016892,   
        "probe_ids": [1,2,3,4]
    }

    is_success, results = AtlasLatestRequest(**kwargs).create()

    if is_success:
        print(results)


Streaming API
-------------
Atlas supports getting results and other events through a stream to get them close to real time. The stream is implemented using websockets and `socket.io`_ protocol.

Measurement Results
^^^^^^^^^^^^^^^^^^^
Besides fetching results from main API it is possible to get results though streaming API. You have to use AtlasStream object and bind to "result" channel. You can start the a result stream by specifying at least the measurement ID in the stream parameters.
More details on the available parameters of the stream can be found on the `streaming documentation`_.

Example:

.. code:: python

    from ripe.atlas.cousteau import AtlasStream

    def on_result_response(*args):
        """
        Function that will be called every time we receive a new result.
        Args is a tuple, so you should use args[0] to access the real message.
        """
        print args[0]

    atlas_stream = AtlasStream()
    atlas_stream.connect()

    channel = "result"
    # Bind function we want to run with every result message received
    atlas_stream.bind_channel(channel, on_result_response)

    # Subscribe to new stream for 1001 measurement results
    stream_parameters = {"msm": 1001}
    atlas_stream.start_stream(stream_type="result", **stream_parameters)

    # Timeout all subscriptions after 5 secs. Leave seconds empty for no timeout.
    # Make sure you have this line after you start *all* your streams
    atlas_stream.timeout(seconds=5)

    # Shut down everything
    atlas_stream.disconnect()


Connection Events
^^^^^^^^^^^^^^^^^
Besides results, streaming API supports also probe's connect/disconnect events. Again you have to use AtlasStream object but this time you have to bind to "probe" channel.
More info about additional parameters can be found on the `streaming documentation`_.

Example:

.. code:: python

    from ripe.atlas.cousteau import AtlasStream

    def on_result_response(*args):
        """
        Function that will be called every time we receive a new event.
        Args is a tuple, so you should use args[0] to access the real event.
        """
        print args[0]

    atlas_stream = AtlasStream()
    atlas_stream.connect()

    # Probe's connection status results
    channel = "probe"
    atlas_stream.bind_channel(channel, on_result_response)
    stream_parameters = {"enrichProbes": True}
    atlas_stream.start_stream(stream_type="probestatus", **stream_parameters)

    # Timeout all subscriptions after 5 secs. Leave seconds empty for no timeout.
    # Make sure you have this line after you start *all* your streams
    atlas_stream.timeout(seconds=5)
    # Shut down everything
    atlas_stream.disconnect()


.. _socket.io: http://socket.io/
.. _streaming documentation: https://atlas.ripe.net/docs/result-streaming/


Using Sagan Library
-------------------
In case you need to do further processing with any of the results you can use our official RIPE Atlas results parsing library called `Sagan`_.
An example of how to combine two libraries is the below:

.. code:: python

    from ripe.atlas.cousteau import AtlasLatestRequest
    from ripe.atlas.sagan import Result

    kwargs = {
        "probe_ids": [1,2,3,4]
    }

    is_success, results = AtlasLatestRequest(**kwargs).create()

    if is_success:
        for result in results:
            print(Result.get(result))

.. _Sagan: https://github.com/RIPE-NCC/ripe.atlas.sagan


Metadata
========
RIPE Atlas API allows you to get metadata about probes and measurements in the system. You can get metadata for a single object or filter based on various criteria.

Single Objects
--------------
Every time you create a new instance of either Measurement/Probe objects it will fetch meta data from API and return an object with selected attributes.

Measurement
^^^^^^^^^^^
Using the Measurement object will allow you to have a python object with attributes populated from specific measurement's meta data.

Example:

.. code:: python

    from ripe.atlas.cousteau import Measurement

    measurement = Measurement(id=1000002)
    print(measurement.protocol)
    print(measurement.description)
    print(measurement.is_oneoff)
    print(measurement.is_public)
    print(measurement.target_ip)
    print(measurement.target_asn)
    print(measurement.type)
    print(measurement.interval)
    print(dir(measurement)) # Full list of properties

Probe
^^^^^
Using the Probe object will allow you to have a python object with attributes populated from specific probe's meta data.

.. code:: python

    from ripe.atlas.cousteau import Probe

    probe = Probe(id=3)
    print(probe.country_code)
    print(probe.is_anchor)
    print(probe.is_public)
    print(probe.address_v4)
    print(dir(probe)) # Full list of properties


Filtering
---------
This feature queries API for probes/measurements based on specified filters. Filters
should be according to `filter api documentation`_. Underneath it will follow all next urls until there are no more objects. It returns a python generator that you can use in a for loop to access each object.

Probe
^^^^^
The following example will fetch all measurements with Status equals to "Specified". More info on filters for these call are on `probe's filtering documentation`_.

.. code:: python

    from ripe.atlas.cousteau import ProbeRequest

    filters = {"tags": "NAT", "country_code": "NL", "asn_v4": "3333"}
    probes = ProbeRequest(**filters)

    for probe in probes:
        print(probe["id"])

    # Print total count of found probes
    print(probes.total_count)


Measurement
^^^^^^^^^^^
The following example will fetch all probes from NL with asn\_v4 3333 and with tag NAT. More info on filters for these call are on `measurement's filtering documentation`_.

.. code:: python

    from ripe.atlas.cousteau import MeasurementRequest

    filters = {"status": 1}
    measurements = MeasurementRequest(**filters)

    for msm in measurements:
        print(msm["id"])

    # Print total count of found measurements
    print(measurements.total_count)


.. _filter api documentation: https://atlas.ripe.net/docs/rest/
.. _measurement's filtering documentation: https://atlas.ripe.net/docs/rest/#measurement
.. _probe's filtering documentation: https://atlas.ripe.net/docs/rest/#probe


General GET API Requests
========================
Using the general AtlasRequest object you can do any GET request to the RIPE Atlas API considering you provide the url path.

Example:

.. code:: python

    url_path = "/api/v2/anchors"
    request = AtlasRequest(**{"url_path": url_path})
    result = namedtuple('Result', 'success response')
    (is_success, response) = request.get()
    if not is_success:
        return False

    return result.response["participant_count"]


.. _documentation pages: https://atlas.ripe.net/docs/measurement-creation-api/
.. _docs: https://atlas.ripe.net/docs/rest/#participation-request
.. _API key: https://atlas.ripe.net/docs/keys/
