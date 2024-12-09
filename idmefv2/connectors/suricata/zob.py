import unittest
from idmefv2.connectors.suricata.idmefv2_converter import IDMEFv2Converter

class TestIDMEFv2Converter(unittest.TestCase):

    EVE_INPUT = {
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

    def test_1(self):
        converter = IDMEFv2Converter()
        o = converter.convert(self.EVE_INPUT)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['Version'], '2.0.3')
