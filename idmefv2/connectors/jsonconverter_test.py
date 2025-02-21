from .jsonconverter import JSONConverter

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
