'''
The clamav to IDMEFv2 convertor.
'''
from copy import deepcopy
from datetime import datetime
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid, idmefv2_my_local_ip

def _create_time():
    return datetime.now().astimezone().isoformat()

def _find_virus(x: any):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == 'Viruses':
                return v
            if k == 'Alerts':
                return [alert['Name'] for alert in v if 'Name' in alert]
            r = _find_virus(v)
            if r is not None:
                return r
    elif isinstance(x, list):
        for v in x:
            r = _find_virus(v)
            if r is not None:
                return r
    return None

def _viruses(x):
    v = _find_virus(x)
    return 'Virus found: ' + ', '.join(v) if v else 'Unknown'

def _md5_hash(x):
    md5 = x.get('md5', x.get('FileMD5'))
    if md5 is None:
        return None
    return 'md5:' + md5

def _sha256_hash(x):
    sha256 = x.get('sha256', x.get('SHA256'))
    if sha256 is None:
        return None
    return 'sha256:' + sha256

# pylint: disable=too-few-public-methods
class ClamavConverter(JSONConverter):
    '''
    A class converting clamav metadata.json to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V08',
        'ID': idmefv2_uuid,
        'CreateTime': _create_time,
        'Category': ['Malware.Other'],
        'Priority': 'High',
        'Description' : 'Virus found',
        "Type": ["Cyber"],
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "clamav",
            "Model": "Clamav Antivirus",
            "Category": [
                "END.AV"
            ],
            "Data": [
                "File"
            ],
            "Method": [
                "Signature"
            ]
        },
        "Attachment": [
            {
                "Name": "virus",
                "FileName": "$.FileName",
                "Hash": [
                ],
                "Size": (int, "$.FileSize"),
                "Note": (_viruses, "$"),
            },
        ],
    }

    def __init__(self):
        super().__init__(ClamavConverter.IDMEFV2_TEMPLATE)

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
        if not self.filter(src):
            return (False, src)

        template = deepcopy(self.IDMEFV2_TEMPLATE)
        md5 = _md5_hash(src)
        sha256 = _sha256_hash(src)
        if md5 is None and sha256 is None:
            template['Attachment'][0].pop('Hash')
        else:
            if (md5 is not None):
                template['Attachment'][0]['Hash'].append(md5)
            if (sha256 is not None):
                template['Attachment'][0]['Hash'].append(sha256)

        return JSONConverter(template).convert(src)
