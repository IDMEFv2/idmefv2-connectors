'''
The clamav to IDMEFv2 convertor.
'''
from datetime import datetime
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid

def _create_time():
    '''
    Returns current date and time in ISO 8601 format, including timezone
    '''
    return datetime.now().astimezone().isoformat()

def _find_virus(x: any):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == 'Viruses':
                return v
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
    return 'Virus found: ' + ', '.join(_find_virus(x)) if v is not None else 'Unknown'

# pylint: disable=too-few-public-methods
class ClamavConverter(JSONConverter):
    '''
    A class converting clamav metadata.json to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': _create_time,
        'Category': ['Malicious.System'],
        'Priority': 'High',
        'Description' : 'Virus found',
        "Analyzer": {
            "IP": "127.0.0.1",
            "Name": "clamav",
            "Model": "Clamav Antivirus",
            "Type": "Cyber",
            "Category": [
                "AV"
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
                    ((lambda x : 'md5:' + x), "$.FileMD5"),
                ],
                "Size": (int, "$.FileSize"),
                "Note": (_viruses, "$"),

            },
        ],
    }

    def __init__(self):
        super().__init__(ClamavConverter.IDMEFV2_TEMPLATE)
