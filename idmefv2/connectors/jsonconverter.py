'''
    Generic JSON to JSON converter
'''
import jsonpath_ng as jsonpath

class JSONConverter(object):

    @staticmethod
    def __compile_template(template: any):
        '''
            Compile JSON Path elements contained in template

            Parameters:
                template(dict): the template of conversion output
            Returns: the compiled template
        '''
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
            Initialize converter by parsing JSON Path elements contained in template

            Parameters:
                template(dict): the template of conversion output
        '''
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

    def filter(self, src: dict) -> bool:
        '''
            Filters JSON objects that must not be converted

            Sub-classes can overload this method

            Returns: True if JSON object must be converted
        '''
        return True

    def convert(self, src: dict) -> (bool, dict):
        '''
            Convert JSON data to another JSON data

            Parameters:
                src(dict): JSON data, as a dictionary

            Returns: a tuple containing (True, converted JSON) if converted, (False, src) if not
        '''
        if self.filter(src):
            return (True, JSONConverter.__convert(self._compiled_template, src))
        return (False, src)