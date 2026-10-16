'''
The clamav to IDMEFv2 convertor.
'''
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
        raise ValueError('ClamAV metadata is missing md5 and FileMD5')
    return 'md5:' + md5

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
                    (_md5_hash, "$"),
                ],
                "Size": (int, "$.FileSize"),
                "Note": (_viruses, "$"),
            },
        ],
    }

    def __init__(self):
        super().__init__(ClamavConverter.IDMEFV2_TEMPLATE)
