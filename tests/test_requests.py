import mock
import unittest
import requests
from datetime import datetime

from jsonschema import validate

from ripe.atlas.cousteau.version import __version__
from ripe.atlas.cousteau import (
    Ping, AtlasSource, AtlasChangeSource, AtlasCreateRequest,
    AtlasChangeRequest, AtlasLatestRequest, AtlasResultsRequest,
    RequestGenerator, ProbeRequest, Probe, Measurement, AtlasRequest
)
from ripe.atlas.cousteau.exceptions import APIResponseError
from . import post_data_create_schema, post_data_change_schema


class FakeResponse(object):
    def __init__(self, json_return={}, ok=True):
        self.json_return = json_return
        self.ok = ok
        self.text = "testing"

    def json(self):
        return self.json_return


class FakeErrorResponse(FakeResponse):
    def json(self):
        raise ValueError("json breaks")


class TestAtlasRequest(unittest.TestCase):
    def setUp(self):
        self.request = AtlasRequest(**{
            "key": "blaaaa",
            "server": "test",
            "url_path": "testing"
        })

    def test_headers(self):
        """Tests header fields of the request."""
        expected_output = {
            "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.assertEqual(expected_output, self.request.get_headers())

    def test_http_method_args(self):
        """Tests initial args that will be passed later to HTTP method."""
        expected_output = {
            "params": {"key": "blaaaa"},
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }
        self.assertEqual(expected_output, self.request.http_method_args)

    def test_get_method(self):
        """Tests GET reuest method"""
        extra_params = {"bull": "shit", "cow": "shit", "horse": "shit"}
        expected_args = {
            "params": {
                "key": "blaaaa", "bull": "shit",
                "cow": "shit", "horse": "shit"
            },
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.http_method') as mock_get:
            mock_get.return_value = True
            self.request.get(**extra_params)
            self.assertEqual(self.request.http_method_args, expected_args)

    def test_url_build(self):
        """Tests build of the url of the request."""
        self.request.build_url()
        self.assertEqual(self.request.url, "https://testtesting")

    def test_success_http_method(self):
        """Tests the main http method function of the request in case of success"""
        with mock.patch('ripe.atlas.cousteau.AtlasRequest.get_http_method') as mock_get:
            fake = FakeResponse(json_return={"blaaa": "b"})
            mock_get.return_value = fake
            self.assertEqual(
                self.request.http_method("GET"),
                (True, {"blaaa": "b"})
            )

            fake_error = FakeErrorResponse()
            mock_get.return_value = fake_error
            self.assertEqual(
                self.request.http_method("GET"),
                (True, "testing")
            )

    def test_not_success_http_method(self):
        """Tests the main http method function of the request in case of fail"""
        with mock.patch('ripe.atlas.cousteau.AtlasRequest.get_http_method') as mock_get:
            fake = FakeResponse(json_return={"blaaa": "b"}, ok=False)
            mock_get.return_value = fake
            self.assertEqual(
                self.request.http_method("GET"),
                (False, {"blaaa": "b"})
            )

            fake_error = FakeErrorResponse(ok=False)
            mock_get.return_value = fake_error
            self.assertEqual(
                self.request.http_method("GET"),
                (False, "testing")
            )

    def test_exception_http_method(self):
        """Tests the main http method function of the request in case of fail"""
        with mock.patch('ripe.atlas.cousteau.AtlasRequest.get_http_method') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("excargs")
            self.assertEqual(
                self.request.http_method("GET"),
                (False, ("excargs",))
            )

    def test_user_agent(self):
        with mock.patch("ripe.atlas.cousteau.request.__version__", 999):
            standard = "RIPE ATLAS Cousteau v999"
            self.assertEqual(AtlasRequest().http_agent, standard)
            self.assertEqual(AtlasRequest(user_agent=None).http_agent, standard)
            self.assertEqual(AtlasRequest(user_agent="w00t").http_agent, "w00t")


class TestAtlasCreateRequest(unittest.TestCase):
    def setUp(self):
        self.create_source = AtlasSource(
            **{"type": "area", "value": "WW", "requested": 3}
        )
        self.measurement = Ping(**{
            "target": "testing", "af": 6,
            "description": "testing"
        })
        self.request = AtlasCreateRequest(**{
            "start_time": datetime(2015, 10, 16),
            "stop_time": 1445040000,
            "key": "path_to_key",
            "measurements": [self.measurement],
            "sources": [self.create_source],
            "is_oneoff": True,
        })

    def test_construct_post_data(self):
        """Tests construction of past data"""
        self.request._construct_post_data()
        validate(self.request.post_data, post_data_create_schema)

    def test_post_method(self):
        """Tests POST reuest method"""
        self.maxDiff = None
        expected_args = {
            "json": {
                "definitions": [{
                    "af": 6, "description": "testing",
                    "target": "testing", "type": "ping"
                }],
                "is_oneoff": True,
                "probes": [{"requested": 3, "type": "area", "value": "WW"}],
                "start_time": 1444953600,
                "stop_time": 1445040000
            },
            "params": {"key": "path_to_key"},
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.http_method') as mock_get:
            self.request._construct_post_data()
            mock_get.return_value = True
            self.request.post()
            self.assertEqual(self.request.http_method_args, expected_args)

    def test_post_method_without_times(self):
        """Tests POST reuest method without any time specified"""
        request = AtlasCreateRequest(**{
            "key": "path_to_key",
            "measurements": [self.measurement],
            "sources": [self.create_source],
        })
        self.maxDiff = None
        expected_args = {
            "json": {
                "definitions": [{
                    "af": 6, "description": "testing",
                    "target": "testing", "type": "ping"
                }],
                "is_oneoff": False,
                "probes": [{"requested": 3, "type": "area", "value": "WW"}],
            },
            "params": {"key": "path_to_key"},
            "headers": {
                "User-Agent": "RIPE ATLAS Cousteau v{0}".format(__version__),
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        }
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.http_method') as mock_get:
            request._construct_post_data()
            mock_get.return_value = True
            request.post()
            self.assertEqual(request.http_method_args, expected_args)


class TestAtlasChangeRequest(unittest.TestCase):
    def setUp(self):
        change_source = AtlasChangeSource(
            **{"value": "WW", "requested": 3, "action": "add", "type": "area"}
        )
        self.request = AtlasChangeRequest(**{
            "msm_id": 1, "sources": [change_source]
        })

    def test_construct_post_data(self):
        self.request._construct_post_data()
        validate(self.request.post_data, post_data_change_schema)


class TestAtlasResultsRequest(unittest.TestCase):

    def test_url_path_and_params(self):
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27",
            "stop": "2011-11-27 01",
            "probe_ids": [1, 2, 3]
        })
        self.assertEqual(
            request.url_path, "/api/v2/measurements/1000002/results"
        )
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            set(query_filters.keys()), set(["key", "stop", "start", "probe_ids"])
        )
        self.assertEqual(query_filters["start"], 1322352000)
        self.assertEqual(query_filters["stop"], 1322355600)
        self.assertEqual(
            query_filters["probe_ids"], "1,2,3"
        )

    def test_probe_ids_query_params(self):
        """Tests probe_ids as query params for different entries"""
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "probe_ids": [1, 2, 3]
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            query_filters["probe_ids"], "1,2,3"
        )

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "probe_ids": "15,  2,3"
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            query_filters["probe_ids"], "15,  2,3"
        )

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "probe_ids": 15
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(
            query_filters["probe_ids"], 15
        )

    def test_start_time_query_params(self):
        """Tests start time as query params for different entries"""
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": "2011-11-27 01:01",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322355660)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": 1322352000,
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "start": datetime(2011, 11, 27)
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["start"], 1322352000)

    def test_stop_time_query_params(self):
        """Tests stop time as query params for different entries"""
        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": "2011-11-27",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": "2011-11-27 01:01",
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322355660)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": 1322352000,
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322352000)

        request = AtlasResultsRequest(**{
            "msm_id": 1000002,
            "stop": datetime(2011, 11, 27)
        })
        query_filters = request.http_method_args["params"]
        self.assertEqual(query_filters["stop"], 1322352000)


class TestAtlasLatestRequest(unittest.TestCase):

    def test_url_path(self):
        """Tests construction of path."""
        self.assertEqual(
            AtlasLatestRequest(msm_id=1001).url_path,
            "/api/v2/measurements/1001/latest"
        )
        self.assertEqual(
            AtlasLatestRequest(msm_id=1002, probe_ids=[1, 2, 3]).url_path,
            "/api/v2/measurements/1002/latest"
        )

    def test_query_params(self):
        """Tests construction of query parameters."""
        self.assertEqual(
            AtlasLatestRequest(
                msm_id=1001, probe_ids=(1, 2, 3, 24)
            ).http_method_args["params"],
            {"key": None, "probe_ids": "1,2,3,24"}
        )
        self.assertEqual(
            AtlasLatestRequest(
                msm_id=1001, probe_ids="1, 2, 3, 24"
            ).http_method_args["params"],
            {"key": None, "probe_ids": "1, 2, 3, 24"}
        )


class TestRequestGenerator(unittest.TestCase):
    def test_build_url(self):

        def decostruct_url_params(url_params):
            """
            Pure man's way of splitting args to avoid unpredicted output
            from python hashed dict keys
            """
            params = url_params.split("&")
            params[0] = params[0][1:]
            return set(params)

        kwargs = {"limit": "100", "asn": "3333"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            decostruct_url_params(r.build_url()), set(["limit=100", "asn=3333"])
        )
        kwargs = {"limit": "100", "asn": "3333", "tags": "NAT,system-ipv4-works"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            decostruct_url_params(r.build_url()),
            set(["limit=100", "tags=NAT,system-ipv4-works", "asn=3333"])
        )
        kwargs = {"asn": "3333"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?asn=3333"
        )
        kwargs = {"limit": "10"}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), "?limit=10"
        )
        kwargs = {}
        r = RequestGenerator(**kwargs)
        self.assertEqual(
            r.build_url(), ""
        )

    def test_wrong_id_filter(self):
        arequest = mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get').start()
        arequest.return_value = False, {}
        kwargs = {"id__in": range(1, 10)}
        r = ProbeRequest(**kwargs)
        self.assertRaises(APIResponseError, lambda: list(r))

    def test_long_id_filter(self):
        kwargs = {"id__in": ",".join(map(str, range(1, 2000)))}
        r = ProbeRequest(**kwargs)
        expected_list = ['/api/v2/probes/?id__in=501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801,802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,819,820,821,822,823,824,825,826,827,828,829,830,831,832,833,834,835,836,837,838,839,840,841,842,843,844,845,846,847,848,849,850,851,852,853,854,855,856,857,858,859,860,861,862,863,864,865,866,867,868,869,870,871,872,873,874,875,876,877,878,879,880,881,882,883,884,885,886,887,888,889,890,891,892,893,894,895,896,897,898,899,900,901,902,903,904,905,906,907,908,909,910,911,912,913,914,915,916,917,918,919,920,921,922,923,924,925,926,927,928,929,930,931,932,933,934,935,936,937,938,939,940,941,942,943,944,945,946,947,948,949,950,951,952,953,954,955,956,957,958,959,960,961,962,963,964,965,966,967,968,969,970,971,972,973,974,975,976,977,978,979,980,981,982,983,984,985,986,987,988,989,990,991,992,993,994,995,996,997,998,999,1000', '/api/v2/probes/?id__in=1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,1012,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,1071,1072,1073,1074,1075,1076,1077,1078,1079,1080,1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,1092,1093,1094,1095,1096,1097,1098,1099,1100,1101,1102,1103,1104,1105,1106,1107,1108,1109,1110,1111,1112,1113,1114,1115,1116,1117,1118,1119,1120,1121,1122,1123,1124,1125,1126,1127,1128,1129,1130,1131,1132,1133,1134,1135,1136,1137,1138,1139,1140,1141,1142,1143,1144,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,1155,1156,1157,1158,1159,1160,1161,1162,1163,1164,1165,1166,1167,1168,1169,1170,1171,1172,1173,1174,1175,1176,1177,1178,1179,1180,1181,1182,1183,1184,1185,1186,1187,1188,1189,1190,1191,1192,1193,1194,1195,1196,1197,1198,1199,1200,1201,1202,1203,1204,1205,1206,1207,1208,1209,1210,1211,1212,1213,1214,1215,1216,1217,1218,1219,1220,1221,1222,1223,1224,1225,1226,1227,1228,1229,1230,1231,1232,1233,1234,1235,1236,1237,1238,1239,1240,1241,1242,1243,1244,1245,1246,1247,1248,1249,1250,1251,1252,1253,1254,1255,1256,1257,1258,1259,1260,1261,1262,1263,1264,1265,1266,1267,1268,1269,1270,1271,1272,1273,1274,1275,1276,1277,1278,1279,1280,1281,1282,1283,1284,1285,1286,1287,1288,1289,1290,1291,1292,1293,1294,1295,1296,1297,1298,1299,1300,1301,1302,1303,1304,1305,1306,1307,1308,1309,1310,1311,1312,1313,1314,1315,1316,1317,1318,1319,1320,1321,1322,1323,1324,1325,1326,1327,1328,1329,1330,1331,1332,1333,1334,1335,1336,1337,1338,1339,1340,1341,1342,1343,1344,1345,1346,1347,1348,1349,1350,1351,1352,1353,1354,1355,1356,1357,1358,1359,1360,1361,1362,1363,1364,1365,1366,1367,1368,1369,1370,1371,1372,1373,1374,1375,1376,1377,1378,1379,1380,1381,1382,1383,1384,1385,1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1416,1417,1418,1419,1420,1421,1422,1423,1424,1425,1426,1427,1428,1429,1430,1431,1432,1433,1434,1435,1436,1437,1438,1439,1440,1441,1442,1443,1444,1445,1446,1447,1448,1449,1450,1451,1452,1453,1454,1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465,1466,1467,1468,1469,1470,1471,1472,1473,1474,1475,1476,1477,1478,1479,1480,1481,1482,1483,1484,1485,1486,1487,1488,1489,1490,1491,1492,1493,1494,1495,1496,1497,1498,1499,1500', '/api/v2/probes/?id__in=1501,1502,1503,1504,1505,1506,1507,1508,1509,1510,1511,1512,1513,1514,1515,1516,1517,1518,1519,1520,1521,1522,1523,1524,1525,1526,1527,1528,1529,1530,1531,1532,1533,1534,1535,1536,1537,1538,1539,1540,1541,1542,1543,1544,1545,1546,1547,1548,1549,1550,1551,1552,1553,1554,1555,1556,1557,1558,1559,1560,1561,1562,1563,1564,1565,1566,1567,1568,1569,1570,1571,1572,1573,1574,1575,1576,1577,1578,1579,1580,1581,1582,1583,1584,1585,1586,1587,1588,1589,1590,1591,1592,1593,1594,1595,1596,1597,1598,1599,1600,1601,1602,1603,1604,1605,1606,1607,1608,1609,1610,1611,1612,1613,1614,1615,1616,1617,1618,1619,1620,1621,1622,1623,1624,1625,1626,1627,1628,1629,1630,1631,1632,1633,1634,1635,1636,1637,1638,1639,1640,1641,1642,1643,1644,1645,1646,1647,1648,1649,1650,1651,1652,1653,1654,1655,1656,1657,1658,1659,1660,1661,1662,1663,1664,1665,1666,1667,1668,1669,1670,1671,1672,1673,1674,1675,1676,1677,1678,1679,1680,1681,1682,1683,1684,1685,1686,1687,1688,1689,1690,1691,1692,1693,1694,1695,1696,1697,1698,1699,1700,1701,1702,1703,1704,1705,1706,1707,1708,1709,1710,1711,1712,1713,1714,1715,1716,1717,1718,1719,1720,1721,1722,1723,1724,1725,1726,1727,1728,1729,1730,1731,1732,1733,1734,1735,1736,1737,1738,1739,1740,1741,1742,1743,1744,1745,1746,1747,1748,1749,1750,1751,1752,1753,1754,1755,1756,1757,1758,1759,1760,1761,1762,1763,1764,1765,1766,1767,1768,1769,1770,1771,1772,1773,1774,1775,1776,1777,1778,1779,1780,1781,1782,1783,1784,1785,1786,1787,1788,1789,1790,1791,1792,1793,1794,1795,1796,1797,1798,1799,1800,1801,1802,1803,1804,1805,1806,1807,1808,1809,1810,1811,1812,1813,1814,1815,1816,1817,1818,1819,1820,1821,1822,1823,1824,1825,1826,1827,1828,1829,1830,1831,1832,1833,1834,1835,1836,1837,1838,1839,1840,1841,1842,1843,1844,1845,1846,1847,1848,1849,1850,1851,1852,1853,1854,1855,1856,1857,1858,1859,1860,1861,1862,1863,1864,1865,1866,1867,1868,1869,1870,1871,1872,1873,1874,1875,1876,1877,1878,1879,1880,1881,1882,1883,1884,1885,1886,1887,1888,1889,1890,1891,1892,1893,1894,1895,1896,1897,1898,1899,1900,1901,1902,1903,1904,1905,1906,1907,1908,1909,1910,1911,1912,1913,1914,1915,1916,1917,1918,1919,1920,1921,1922,1923,1924,1925,1926,1927,1928,1929,1930,1931,1932,1933,1934,1935,1936,1937,1938,1939,1940,1941,1942,1943,1944,1945,1946,1947,1948,1949,1950,1951,1952,1953,1954,1955,1956,1957,1958,1959,1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999']
        self.assertEqual(r.split_urls, expected_list)

    def test_sane_output(self):
        arequest = mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get').start()
        arequest.return_value = True, {
            "count": "3",
            "next": None,
            "results": [
                {
                    "address_v4": None,
                    "address_v6": None,
                    "asn_v4": None,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 90,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v4": None,
                    "prefix_v6": None,
                    "status": 3,
                    "tags": [
                        "home",
                        "nat",
                    ],
                    "latitude": 37.4675,
                    "longitude": 22.4015,
                    "status_name": "Abandoned",
                    "status_since": 1376578323
                },
                {
                    "asn_v4": 3329,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 268,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v6": None,
                    "status": 1,
                    "tags": [
                        "system-ipv6-ula",
                        "system-ipv4-rfc1918"
                    ],
                    "latitude": 40.6415,
                    "longitude": 22.9405,
                    "status_name": "Connected",
                    "status_since": 1433248709
                }
            ]
        }
        probe_generator = ProbeRequest(**{})
        probes_list = list(probe_generator)
        expected_value = [
            {
                "address_v4": None,
                "address_v6": None,
                "asn_v4": None,
                "asn_v6": None,
                "country_code": "GR",
                "id": 90,
                "is_anchor": False,
                "is_public": False,
                "prefix_v4": None,
                "prefix_v6": None,
                "status": 3,
                "tags": [
                    "home",
                    "nat",
                ],
                "latitude": 37.4675,
                "longitude": 22.4015,
                "status_name": "Abandoned",
                "status_since": 1376578323
            },
            {
                "asn_v4": 3329,
                "asn_v6": None,
                "country_code": "GR",
                "id": 268,
                "is_anchor": False,
                "is_public": False,
                "prefix_v6": None,
                "status": 1,
                "tags": [
                    "system-ipv6-ula",
                    "system-ipv4-rfc1918"
                ],
                "latitude": 40.6415,
                "longitude": 22.9405,
                "status_name": "Connected",
                "status_since": 1433248709
            }
        ]

        self.assertEqual(probes_list, expected_value)
        self.assertEqual(probe_generator.total_count, 3)

    def test_wrong_api_output(self):
        arequest = mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get').start()
        arequest.return_value = True, {}
        probe_generator = ProbeRequest(**{})
        probes_list = list(probe_generator)
        expected_value = []

        self.assertEqual(probes_list, expected_value)
        self.assertEqual(probe_generator.total_count, 0)

    def test_semisane_output(self):
        arequest = mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get').start()
        first_get_resp = (True, {
            "count": "6",
            "next": "blaaaaaah",
            "results": [
                {
                    "address_v4": None,
                    "address_v6": None,
                    "asn_v4": None,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 90,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v4": None,
                    "prefix_v6": None,
                    "status": 3,
                    "tags": [
                        "home",
                        "nat",
                    ],
                    "latitude": 37.4675,
                    "longitude": 22.4015,
                    "status_name": "Abandoned",
                    "status_since": 1376578323
                },
                {
                    "asn_v4": 3329,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 268,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v6": None,
                    "status": 1,
                    "tags": [
                        "system-ipv6-ula",
                        "system-ipv4-rfc1918"
                    ],
                    "latitude": 40.6415,
                    "longitude": 22.9405,
                    "status_name": "Connected",
                    "status_since": 1433248709
                }
            ]
        })
        second_get_resp = (True, {
            "count": "5",
            "next": None,
            "results": [
                {
                    "address_v4": None,
                    "address_v6": None,
                    "asn_v4": None,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 99,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v4": None,
                    "prefix_v6": None,
                    "status": 3,
                    "tags": [
                        "home",
                        "nat",
                    ],
                    "latitude": 37.4675,
                    "longitude": 22.4015,
                    "status_name": "Abandoned",
                    "status_since": 1376578323
                },
                {
                    "asn_v4": 3329,
                    "asn_v6": None,
                    "country_code": "GR",
                    "id": 269,
                    "is_anchor": False,
                    "is_public": False,
                    "prefix_v6": None,
                    "status": 1,
                    "tags": [
                        "system-ipv6-ula",
                        "system-ipv4-rfc1918"
                    ],
                    "latitude": 40.6415,
                    "longitude": 22.9405,
                    "status_name": "Connected",
                    "status_since": 1433248709
                }
            ]
        })
        arequest.side_effect = [first_get_resp, second_get_resp]
        probe_generator = ProbeRequest(**{})
        probes_list = list(probe_generator)
        expected_value = [
            {
                "address_v4": None,
                "address_v6": None,
                "asn_v4": None,
                "asn_v6": None,
                "country_code": "GR",
                "id": 90,
                "is_anchor": False,
                "is_public": False,
                "prefix_v4": None,
                "prefix_v6": None,
                "status": 3,
                "tags": [
                    "home",
                    "nat",
                ],
                "latitude": 37.4675,
                "longitude": 22.4015,
                "status_name": "Abandoned",
                "status_since": 1376578323
            },
            {
                "asn_v4": 3329,
                "asn_v6": None,
                "country_code": "GR",
                "id": 268,
                "is_anchor": False,
                "is_public": False,
                "prefix_v6": None,
                "status": 1,
                "tags": [
                    "system-ipv6-ula",
                    "system-ipv4-rfc1918"
                ],
                "latitude": 40.6415,
                "longitude": 22.9405,
                "status_name": "Connected",
                "status_since": 1433248709
            },
            {
                "address_v4": None,
                "address_v6": None,
                "asn_v4": None,
                "asn_v6": None,
                "country_code": "GR",
                "id": 99,
                "is_anchor": False,
                "is_public": False,
                "prefix_v4": None,
                "prefix_v6": None,
                "status": 3,
                "tags": [
                    "home",
                    "nat",
                ],
                "latitude": 37.4675,
                "longitude": 22.4015,
                "status_name": "Abandoned",
                "status_since": 1376578323
            },
            {
                "asn_v4": 3329,
                "asn_v6": None,
                "country_code": "GR",
                "id": 269,
                "is_anchor": False,
                "is_public": False,
                "prefix_v6": None,
                "status": 1,
                "tags": [
                    "system-ipv6-ula",
                    "system-ipv4-rfc1918"
                ],
                "latitude": 40.6415,
                "longitude": 22.9405,
                "status_name": "Connected",
                "status_since": 1433248709
            }
        ]

        self.assertEqual(probes_list, expected_value)
        self.assertEqual(probe_generator.total_count, 6)

    def tearDown(self):
        mock.patch.stopall()


class TestProbeRepresentation(unittest.TestCase):
    def test_sane_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            resp = {
                "address_v4": "62.194",
                "address_v6": None,
                "asn_v4": 68,
                "asn_v6": None,
                "country_code": "ND",
                "id": 1,
                "is_anchor": False,
                "is_public": False,
                "prefix_v4": "62.194.0.0/16",
                "prefix_v6": None,
                "tags": ["cable"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.8875, 52.3875]
                },
                "status": {
                    "since": "2015-09-28T13:25:16",
                    "id": 1,
                    "name": "Connected"
                }
            }
            request_mock.return_value = True, resp
            probe = Probe(id=1)
            self.assertEqual(probe.meta_data, resp)
            self.assertEqual(probe.country_code, "ND")
            self.assertEqual(probe.address_v4, "62.194")
            self.assertEqual(probe.address_v6, None)
            self.assertEqual(probe.asn_v4, 68)
            self.assertEqual(probe.asn_v6, None)
            self.assertEqual(probe.is_anchor, False)
            self.assertEqual(probe.is_public, False)
            self.assertEqual(probe.prefix_v4, "62.194.0.0/16")
            self.assertEqual(probe.prefix_v6, None)
            self.assertEqual(probe.status, "Connected")
            self.assertEqual(probe.tags, ["cable"])
            self.assertEqual(probe.prefix_v6, None)
            self.assertEqual(probe.geometry, {"type": "Point", "coordinates": [4.8875, 52.3875]})

    def test_error_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = False, {}
            self.assertRaises(APIResponseError, lambda: Probe(id=1))


class TestMeasurementRepresentation(unittest.TestCase):
    def test_sane_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            resp = {
                "af": 4,
                "destination_address": "202.73.56.70",
                "destination_asn": 9255,
                "destination_name": "blaaaah",
                "msm_id": 2310448,
                "description": "Blaaaaaaaaaah",
                "is_oneoff": True,
                "is_public": True,
                "interval": 1800,
                "creation_time": 1439379910,
                "resolve_on_probe": False,
                "start_time": 1439379910,
                "stop_time": 1439380502,
                "status": {"id": 4, "name": "Stopped"},
                "resolved_ips": ["202.73.56.70"],
                "type": {"id": 8, "name": "http", "af": 4},
                "result": "/api/v1/measurement/2310448/result/"
            }
            request_mock.return_value = True, resp
            measurement = Measurement(id=1)
            self.assertEqual(measurement.meta_data, resp)
            self.assertEqual(measurement.protocol, 4)
            self.assertEqual(measurement.destination_address, "202.73.56.70")
            self.assertEqual(measurement.destination_asn, 9255)
            self.assertEqual(measurement.destination_name, "blaaaah")
            self.assertEqual(measurement.description, "Blaaaaaaaaaah")
            self.assertEqual(measurement.is_oneoff, True)
            self.assertEqual(measurement.is_public, True)
            self.assertEqual(measurement.interval, 1800)
            self.assertEqual(measurement.status, "Stopped")
            self.assertEqual(measurement.creation_time, datetime.fromtimestamp(1439379910))
            self.assertEqual(measurement.start_time, datetime.fromtimestamp(1439379910))
            self.assertEqual(measurement.stop_time, datetime.fromtimestamp(1439380502))
            self.assertEqual(measurement.type, "HTTP")
            self.assertEqual(measurement.result_url, "/api/v1/measurement/2310448/result/")

    def test_error_response(self):
        with mock.patch('ripe.atlas.cousteau.request.AtlasRequest.get') as request_mock:
            request_mock.return_value = False, {}
            self.assertRaises(APIResponseError, lambda: Measurement(id=1))
