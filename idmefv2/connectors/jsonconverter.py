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
        return template

    def __init__(self, template: dict):
        '''
            Initialize converter by parsing JSON Path elements contained in template

            Parameters:
                template(dict): the template of conversion output
        '''
        self._compiled_template = JSONConverter.__compile_template(template)

    @staticmethod
    def __convert(template: any, src: dict) -> any:
        if isinstance(template, jsonpath.JSONPath):
            return template.find(src)[0].value
        if isinstance(template, str):
            return template
        if callable(template):
            return template()
        if isinstance(template, dict):
            ret = {k: JSONConverter.__convert(v, src) for (k, v) in template.items()}
            return ret
        if isinstance(template, list):
            ret = [JSONConverter.__convert(v, src) for v in template]
            return ret
        return None

    def convert(self, src: dict) -> dict:
        '''
            Convert JSON data to another JSON data

            Parameters:
                src(dict): JSON data, as a dictionary

            Returns: converted JSON data
        '''
        return JSONConverter.__convert(self._compiled_template, src)
