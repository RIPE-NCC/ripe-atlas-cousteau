Releases History
================
0.10.1 (released 2015-10-06)
----------------------------
New features:
~~~~~~~~~~~~~
- Implement support for object return in the request generators for probe/measurement.

Changes:
~~~~~~~~
- Probe/Measurement python representation takes meta data from v2 API as well. Now everything should point to v2 API.

0.10 (released 2015-10-01)
--------------------------
New features:
~~~~~~~~~~~~~
- add object representation of meta data for a probe or a measurement.

Changes:
~~~~~~~~
- Abandon v1 RIPE ATLAS API and use only v2.

Bug fix:
~~~~~~~~
- Fix bug that prevented users from specifying all possible source types when they tried to add more probes to existing measurements.
- Cover case where a user specified really long list of probes/measurements in the ProbeRequest/MeasurementRequest that was causing 'HTTP ERROR 414: Request-URI Too Long'. Additionally, now if API returns error raise an exception instead of stopping iteration.

0.9.2 (released 2015-09-21)
---------------------------
Changes:
~~~~~~~~
- Small refactor of Stream class and manually enforce websockets in SocketIO client

0.9.1 (released 2015-09-03)
---------------------------
Bug fix:
~~~~~~~~
- Fix bug related to binding result atlas stream.

0.9 (released 2015-09-01)
-------------------------
New features:
~~~~~~~~~~~~~
- add support for fetching real time results using RIPE Atlas stream server.
- this version and on will be available on PYPI.

0.8 (released 2015-08-31)
-------------------------
New features:
~~~~~~~~~~~~~
- add support for NTP measurements.

0.7 (released 2015-06-03)
-------------------------
New features:
~~~~~~~~~~~~~
- add support for fetching probes/measurements meta data using python generators.

0.6 (released 2014-06-17)
-------------------------
New features:
~~~~~~~~~~~~~
- add support for querying results based on start/end time, msm_id and probe id.

Changes:
~~~~~~~~
- add http agent according to package version to all requests.

0.5 (released 2014-05-22)
-------------------------
Changes:
~~~~~~~~
- change package structure to comply with the new structure of atlas packages
- add continuous integration support

 - add tests
 - enable travis
 - enable code health checks

- add required files for uploading to github

0.4 (released 2014-03-31)
-------------------------
New features:
~~~~~~~~~~~~~
- add support for stopping a measurement.

0.3 (released 2014-02-25)
-------------------------
New features:
~~~~~~~~~~~~~
- add simple support for HTTP GET queries.

0.2 (released 2014-02-03)
-------------------------
New features:
~~~~~~~~~~~~~
- add support for adding/removing probes API request.

Changes:
~~~~~~~~
- use AtlasCreateRequest instead of AtlasRequest for creating a new measurement.

0.1 (released 2014-01-21)
-------------------------
- Initial release.
