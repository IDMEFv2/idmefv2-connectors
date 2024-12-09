import unittest
from idmefv2.connectors.jsonconverter import JSONConverter

def foobar():
    return 'FOOBAR'

class TestConverter(unittest.TestCase):

    def test_raw(self):
        template = { 'foo': 'bar'}
        converter = JSONConverter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 'bar')

    def test_path(self):
        template = { 'foo': '$.a'}
        converter = JSONConverter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 1)

    def test_function(self):
        template = { 'foo': foobar}
        converter = JSONConverter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 'FOOBAR')

    def test_deep(self):
        template = { 'foo': { 'bar': '$.a'}}
        converter = JSONConverter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo']['bar'], 1)
