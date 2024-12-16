import unittest
from idmefv2.connectors.jsonconverter import JSONConverter

def foobar():
    return 'FOOBAR'

def conv_datetime(dt):
    return dt + '_FOO'

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

    def test_deep_2(self):
        template = { 'foo': [ 'bar', foobar]}
        converter = JSONConverter(template)
        i =  { 'a':  1}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'][0], 'bar')
        self.assertEqual(o['foo'][1], 'FOOBAR')

    def test_function_2(self):
        template = { 'foo': (conv_datetime, '$.timestamp')}
        converter = JSONConverter(template)
        i =  { 'timestamp':  'AAA'}
        o = converter.convert(i)
        self.assertIsInstance(o, dict)
        self.assertEqual(o['foo'], 'AAA_FOO')
