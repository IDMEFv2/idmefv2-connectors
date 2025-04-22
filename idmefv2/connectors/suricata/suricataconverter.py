'''
The Suricata to IDMEFv2 convertor.
'''
import datetime
from ..jsonconverter import JSONConverter
from ..uuid import idmefv2_uuid

def convert_timestamp(ts: str) -> str:
    '''
    Convert Suricata timestamp

    Args:
        ts (str): timestamp in Suricata format

    Returns:
        str: timestamp in IDMEFv2 format
    '''
    i = datetime.datetime.fromisoformat(ts)
    return i.isoformat()

def convert_severity(severity: int) -> str:
    '''
    Converts a Suricata severity to a IDMEFv2 severity

    Args:
        severity (int): the Suricata severity

    Returns:
        str: the IDMEFv2 severity, an enum in IDMEFv2 schema
    '''
    if severity <= 0:
        return 'Unknown'
    if severity > 4:
        return 'High'
    return {1:'Info', 2:'Low', 3:'Medium', 4:'High'}[severity]

def fix_ip(ip: str) -> str:
    '''
    Fix IP if empty

    Args:
        ip (str): IP in Suricata input

    Returns:
        str: same IP if not empty, '127.0.0.1' if empty
    '''
    if ip == '':
        return '127.0.0.1'
    return ip

def fix_protocol(proto: str) -> str:
    '''
    Fix protocol if empty

    Args:
        proto (str): protocol in Suricata input

    Returns:
        str: same protocol if not empty, 'UNKNOWN' if empty
    '''
    if proto == '':
        return 'UNKNOWN'
    return proto

# pylint: disable=too-few-public-methods
class SuricataConverter(JSONConverter):
    '''
    A class converting Suricata EVE format to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (convert_timestamp, '$.timestamp'),
        'Category': ['Recon.Scanning'],
        'Priority': (convert_severity, '$.alert.severity'),
        'Description' : '$.alert.category',
        "Analyzer": {
            "IP": "127.0.0.1",
            "Name": "suricata",
            "Model": "Suricata NIDS",
            "Type": "Cyber",
            "Category": [
                "NIDS"
            ],
            "Data": [
                "Network"
            ],
            "Method": [
                "Signature"
            ]
        },
        'Source': [
            {
                'IP': (fix_ip, '$.src_ip'),
                'Port': [
                    '$.src_port',
                ],
                'Protocol': [
                    (fix_protocol,'$.proto'),
                ],
            },
        ],
        'Target': [
            {
                'IP': (fix_ip, '$.dest_ip'),
                'Port': [
                    '$.dest_port',
                ],
            },
        ],
    }

    def __init__(self):
        super().__init__(SuricataConverter.IDMEFV2_TEMPLATE)

    def filter(self, src: dict) -> bool:
        '''
        Filters out some Suricata alerts

        Args:
            src (dict): the Suricata input

        Returns:
            bool: true if src must be converted
        '''
        return ('event_type' in src
                and src['event_type'] == 'alert'
                and 'category' in src['alert']
                and src['alert']['category'] != 'Generic Protocol Command Decode')
