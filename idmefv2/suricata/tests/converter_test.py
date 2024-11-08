import unittest
from idmefv2.suricata.converter import Converter

class TestConverter(unittest.TestCase):

    def test_raw(self):
        template = { 'foo': 'bar'}
        converter = Converter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 'bar')
