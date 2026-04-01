# pylint: disable=missing-function-docstring
'''
Tests for the JSON converter
'''
import pytest
from .jsonconverter import JSONConverter, ChainJSONConverter

def foobar():
    return 'FOOBAR'

def conv_datetime(dt):
    return dt + '_FOO'

def test_raw():
    template = { 'foo': 'bar'}
    converter = JSONConverter(template)
    i =  { 'a':  1}
    _, o = converter.convert(i)
    assert isinstance(o, dict)
    assert o['foo'] == 'bar'

def test_path():
    template = { 'foo': '$.a'}
    converter = JSONConverter(template)
    i =  { 'a':  1}
    _, o = converter.convert(i)
    assert isinstance(o, dict)
    assert o['foo'] == 1

def test_function():
    template = { 'foo': foobar}
    converter = JSONConverter(template)
    i =  { 'a':  1}
    _, o = converter.convert(i)
    assert isinstance(o, dict)
    assert o['foo'] == 'FOOBAR'

def test_deep():
    template = { 'foo': { 'bar': '$.a'}}
    converter = JSONConverter(template)
    i =  { 'a':  1}
    _, o = converter.convert(i)
    assert isinstance(o, dict)
    assert o['foo']['bar'] == 1

def test_deep_2():
    template = { 'foo': [ 'bar', foobar]}
    converter = JSONConverter(template)
    i =  { 'a':  1}
    _, o = converter.convert(i)
    assert isinstance(o, dict)
    assert o['foo'][0] == 'bar'
    assert o['foo'][1] == 'FOOBAR'

def test_function_2():
    template = { 'foo': (conv_datetime, '$.timestamp')}
    converter = JSONConverter(template)
    i =  { 'timestamp':  'AAA'}
    _, o = converter.convert(i)
    assert isinstance(o, dict)
    assert o['foo'] == 'AAA_FOO'

def test_chain_converter_1():
    with pytest.raises(TypeError):
        _ = ChainJSONConverter(1, 2)

class _ConverterA(JSONConverter):
    def __init__(self):
        super().__init__({'foo': '$.a'})

    def filter(self, src):
        return 'a' in src

class _ConverterB(JSONConverter):
    def __init__(self):
        super().__init__({'bar': '$.b'})

    def filter(self, src):
        return 'b' in src

def test_chain_converter_2():
    c = ChainJSONConverter(_ConverterA(), _ConverterB())
    _, o = c.convert({'a': 1})
    assert o == {'foo': 1}
    _, o = c.convert({'b': 2})
    assert o == {'bar': 2}
