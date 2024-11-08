import unittest
from idmefv2.suricata.converter import Converter

def foobar():
    return 'FOOBAR'

class TestConverter(unittest.TestCase):

    def test_raw(self):
        template = { 'foo': 'bar'}
        converter = Converter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 'bar')

    def test_path(self):
        template = { 'foo': '$.a'}
        converter = Converter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 1)

    def test_function(self):
        template = { 'foo': foobar}
        converter = Converter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 'FOOBAR')
