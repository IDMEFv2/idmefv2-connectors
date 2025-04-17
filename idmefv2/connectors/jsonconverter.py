'''
    Generic JSON to JSON converter
'''
import jsonpath_ng as jsonpath

class JSONConverter:
    '''
    A class implementing a generic JSON to JSON converter, using a pre-defined template

    This class provides the following methods:
        - constructor: compile the template and store the result
        - convert: convert JSON input using the compiled template
        - filter: filter out JSON input, sub-classes can override this method

    A template can be:
        - a JSON Path (see https://pypi.org/project/jsonpath-ng/ and
        https://goessner.net/articles/JsonPath/), i.e. a string starting by '$'
        - a plain string (not a JSON Path)
        - a dict
        - a list
        - a tuple
        - any other Python type

    Compilation is done by recursive depth-first traversal. For each element in the traversal:
        - if current element is a JSON Path, compile it using jsonpath.parse and produce the
          compiled template
        - if current element is a dict, output a dict having the same keys  and for each key
          the result of the compilation of the associated value (Note: keys are not compiled)
        - if current element is a list, produce a list containing the compilation of all values
        - if element is a tuple, produce a tuple containing the compilation of all values
        - otherwise, produce the current element unchanged

    See jsonconverter_test.py for examples
    '''
    @staticmethod
    def __compile_template(template: any):
        if isinstance(template, str) and template.startswith('$'):
            return jsonpath.parse(template)
        if isinstance(template, dict):
            c = {k: JSONConverter.__compile_template(v) for (k, v) in template.items()}
            return c
        if isinstance(template, list):
            c = [JSONConverter.__compile_template(v) for v in template]
            return c
        if isinstance(template, tuple):
            c = tuple(JSONConverter.__compile_template(v) for v in template)
            return c
        return template

    def __init__(self, template: dict):
        '''
        Initialize converter by compiling the template

        Args:
            template (dict): the template of conversion output
        '''
        self._template = template
        self._compiled_template = JSONConverter.__compile_template(template)

    @staticmethod
    def __is_call(t: any) -> bool:
        if callable(t):
            return True
        if isinstance(t, tuple) and len(t) >= 2 and callable(t[0]):
            return True
        return False

    @staticmethod
    def __call(t: any, src) -> bool:
        if callable(t):
            return t()
        # isinstance(t, tuple) and len(t) >= 2 and callable(t[0]) is True
        fun = t[0]
        args = tuple(JSONConverter.__convert(v, src) for v in t[1:])
        return fun(*args)

    @staticmethod
    def __convert(template: any, src: dict) -> any:
        if isinstance(template, jsonpath.JSONPath):
            return template.find(src)[0].value
        if isinstance(template, str):
            return template
        if JSONConverter.__is_call(template):
            return JSONConverter.__call(template, src)
        if isinstance(template, dict):
            ret = {k: JSONConverter.__convert(v, src) for (k, v) in template.items()}
            return ret
        if isinstance(template, list):
            ret = [JSONConverter.__convert(v, src) for v in template]
            return ret
        return None

    def filter(self, _: dict) -> bool:
        '''
            Filter JSON objects that must not be converted

            Sub-classes can override this method

            Returns: True if JSON object must be converted
        '''
        return True

    def convert(self, src: dict) -> tuple[bool, dict]:
        '''
        Convert JSON data to another JSON data

        Call first filter(src) to check if data must be converted

        Conversion is done by recursive depth-first traversal of the contained compiled template.
        For each element in the traversal:
            - if current element is a JSON Path, call jsonpath.find(src) and output resulting value
            - if current element is a dict, output a dict having the same keys and for each key
            the conversion of the associated value (Note: keys are not converted)
            - if current element is a list, produce a list containing the conversion of all values
            - if current element is a callable, produce the result of calling it
            - if element is a non-empty tuple and its first element is a callable, produce the
              result of calling the first element with arguments the rest of the tuple
            - otherwise, produce the current element unchanged

        Args:
            src (dict): JSON data, as a dict

        Returns:
            tuple[bool, dict]: a tuple containing (True, converted JSON) if converted,
                (False, src) if not
        '''
        if self.filter(src):
            return (True, JSONConverter.__convert(self._compiled_template, src))
        return (False, src)
