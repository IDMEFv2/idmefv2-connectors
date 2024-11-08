'''
    Generic JSON to JSON converter
'''
import jsonpath_ng as jsonpath

class Converter(object):

    @staticmethod
    def __compile_template(template: any):
        '''
            Compile JSON Path elements contained in template

            Parameters:
                template(dict): the template of conversion output
            Returns: the compiled template
        '''
        compiled_template = {}
        for k, v in template.items():
            if isinstance(v, str) and v.startswith('$'):
                compiled_template[k] = jsonpath.parse(v)
            else:
                compiled_template[k] = v
        return compiled_template

    def __init__(self, template: dict):
        '''
            Initialize converter by parsing JSON Path elements contained in template

            Parameters:
                template(dict): the template of conversion output
        '''
        self._compiled_template = Converter.__compile_template(template)

    def convert(self, src: dict) -> dict:
        '''
            Convert JSON data to another JSON data

            Parameters:
                src(dict): JSON data, as a dictionary

            Returns: converted JSON data
        '''
        dest = {}
        for k, v in self._compiled_template.items():
            if isinstance(v, jsonpath.JSONPath):
                dest[k] = v.find(src)[0].value
            elif callable(v):
                dest[k] = v()
            else:
                dest[k] = v
        return dest
