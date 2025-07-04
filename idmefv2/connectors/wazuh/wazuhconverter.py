'''
The wazuh JSON to IDMEFv2 convertor.
'''
#import datetime
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid, idmefv2_convert_timestamp

_LEVELS = {
    0: {'Title': 'Ignored', 'Priority': 'Info'},
    2: {'Title': 'System low priority notification', 'Priority': 'Info'},
    3: {'Title': 'Successful/Authorized events', 'Priority': 'Info'},
    4: {'Title': 'System low priority error', 'Priority': 'Low'},
    5: {'Title': 'User generated error', 'Priority': 'Low'},
    6: {'Title': 'Low relevance attack', 'Priority': 'Low'},
    7: {'Title': '"Bad word" matching', 'Priority': 'Medium'},
    8: {'Title': 'First time seen', 'Priority': 'Medium'},
    9: {'Title': 'Error from invalid source', 'Priority': 'Medium'},
    10: {'Title': 'Multiple user generated errors', 'Priority': 'Medium'},
    11: {'Title': 'Integrity checking warning', 'Priority': 'High'},
    12: {'Title': 'High importance event', 'Priority': 'High'},
    13: {'Title': 'Unusual error (high importance)', 'Priority': 'High'},
    14: {'Title': 'High importance security event', 'Priority': 'High'},
    15: {'Title': 'Severe attack', 'Priority': 'High'},
}

def convert_level(level: int) -> str:
    '''
    Converts a rule level to a IDMEFv2 priority

    Args:
        level (int): the level

    Returns:
        str: the IDMEFv2 priority, an enum in IDMEFv2 schema
    '''
    if level <= 0:
        return 'Unknown'
    if level > 16:
        return 'High'
    return _LEVELS[level]['Priority']

# pylint: disable=too-few-public-methods
class WazuhConverter(JSONConverter):
    '''
    A class converting Wazuh JSON alert format to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (idmefv2_convert_timestamp, '$.timestamp'),
        'Category': ['Information.UnauthorizedModification'],
        'Priority': (convert_level, '$.rule.level'),
        'Description' : '$.rule.description',
        "Analyzer": {
            "IP": "$.agent.ip",
            "Name": "$.agent.name",
            "Model": "Wazuh",
            "Type": "Cyber",
            "Category": [
                "HIDS"
            ],
            "Data": [
                "File"
            ],
            "Method": [
                "Integrity"
            ]
        },
        "Attachment": [
            {
                "Name": "syscheck",
                "FileName": "$.syscheck.path",
                "Hash": [
                    ((lambda h : 'sha-1:' + h), "$.syscheck.sha1_after"),
                    ((lambda h : 'sha-256::' + h), "$.syscheck.sha256_after"),
                ],
                "Size": (int, "$.syscheck.size_after"),
            },
        ],
    }

    def __init__(self):
        super().__init__(WazuhConverter.IDMEFV2_TEMPLATE)

    def filter(self, src: dict) -> bool:
        '''
        Filters out some Wazuh alerts

        Args:
            src (dict): the input

        Returns:
            bool: true if src must be converted
        '''
        return 'syscheck' in src
