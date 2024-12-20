import unittest
from idmefv2.connectors.suricata.suricataconverter import SuricataConverter

class TestSuricataConverter(unittest.TestCase):

    EVE_ALERT_1 = {
        "timestamp": "2017-04-07T22:24:37.251547+0100",
        "flow_id": 586497171462735,
        "pcap_cnt": 53381,
        "event_type": "alert",
        "src_ip": "192.168.2.14",
        "src_port": 50096,
        "dest_ip": "209.53.113.5",
        "dest_port": 80,
        "proto": "TCP",
        "metadata": {
        "flowbits": [
            "http.dottedquadhost"
        ]
        },
        "tx_id": 4,
        "alert": {
        "action": "allowed",
        "gid": 1,
        "signature_id": 2018358,
        "rev": 10,
        "signature": "ET HUNTING GENERIC SUSPICIOUS POST to Dotted Quad with Fake Browser 1",
        "category": "Potentially Bad Traffic",
        "severity": 2
        },
        "app_proto": "http"
    }

    EVE_ALERT_2 = {
        "timestamp":"2024-12-19T17:52:39.590661+0000",
        "flow_id":2102415274651608,
        "in_iface":"wlxc83a35b91aad",
        "event_type":"alert",
        "src_ip":"2600:9000:2662:fa00:0018:30b3:e400:93a1",
        "src_port":80,
        "dest_ip":"2a02:842a:820e:1601:c369:71f8:9da5:c6a4",
        "dest_port":44030,
        "proto":"TCP",
        "pkt_src":"wire/pcap",
        "tx_id":0,
        "tx_guessed":True,
        "alert":{
            "action":"allowed",
            "gid":1,
            "signature_id":2100498,
            "rev":7,
            "signature":"GPL ATTACK_RESPONSE id check returned root",
            "category":"Potentially Bad Traffic",
            "severity":2,
            "metadata":{
                "created_at":["2010_09_23"],
                "signature_severity":["Informational"],
                "updated_at":["2019_07_26"]
                }
            },
        "http":{
            "hostname":"testmynids.org",
            "url":"/uid/index.html",
            "http_user_agent":"curl/8.5.0",
            "http_content_type":"text/html",
            "http_method":"GET",
            "protocol":"HTTP/1.1",
            "status":200,
            "length":39
            },
        "files":[
            {
                "filename":"/uid/index.html",
                "gaps":False,
                "state":"CLOSED",
                "stored":False,
                "size":39,
                "tx_id":0
                }
            ],
        "app_proto":"http",
        "direction":"to_client",
        "flow":{
            "pkts_toserver":6,
            "pkts_toclient":5,
            "bytes_toserver":615,
            "bytes_toclient":976,
            "start":"2024-12-19T17:52:39.555042+0000",
            "src_ip":"2a02:842a:820e:1601:c369:71f8:9da5:c6a4",
            "dest_ip":"2600:9000:2662:fa00:0018:30b3:e400:93a1",
            "src_port":44030,
            "dest_port":80
            }
        }
    EVE_ALERT_3 = {"timestamp":"2024-12-19T17:51:34.369295+0000","in_iface":"wlxc83a35b91aad","event_type":"alert","src_ip":"","src_port":0,"dest_ip":"","dest_port":0,"proto":"","pkt_src":"wire/pcap","alert":{"action":"allowed","gid":1,"signature_id":2200003,"rev":2,"signature":"SURICATA IPv4 truncated packet","category":"Generic Protocol Command Decode","severity":3}}

    EVE_FLOW_1 = {"timestamp":"2024-12-19T17:52:42.249098+0000","flow_id":1909028605511070,"in_iface":"wlxc83a35b91aad","event_type":"flow","src_ip":"54.198.86.24","src_port":443,"dest_ip":"192.168.1.95","dest_port":46106,"proto":"TCP","flow":{"pkts_toserver":10,"pkts_toclient":13,"bytes_toserver":1201,"bytes_toclient":1828,"start":"2024-12-19T17:51:34.247872+0000","end":"2024-12-19T17:51:38.538389+0000","age":4,"state":"new","reason":"timeout","alerted":False},"tcp":{"tcp_flags":"00","tcp_flags_ts":"00","tcp_flags_tc":"00"}}


    def test_1(self):
        converter = SuricataConverter()
        c, o = converter.convert(self.EVE_ALERT_1)
        self.assertTrue(c)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['Version'], '2.D.V04')
        self.assertEqual(o['Source']['Protocol'], 'TCP')

    def test_2(self):
        converter = SuricataConverter()
        c, o = converter.convert(self.EVE_ALERT_2)
        self.assertTrue(c)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['Description'], 'Potentially Bad Traffic')

    def test_3(self):
        converter = SuricataConverter()
        c, o = converter.convert(self.EVE_ALERT_3)
        self.assertTrue(c)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['Description'], 'Generic Protocol Command Decode')

    def test_4(self):
        converter = SuricataConverter()
        c, o = converter.convert(self.EVE_FLOW_1)
        self.assertFalse(c)
