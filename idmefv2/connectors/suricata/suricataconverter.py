import datetime
import uuid
from idmefv2.connectors.jsonconverter import JSONConverter

def idmefv2_uuid():
    return uuid.uuid4().urn[9:]

def convert_timestamp(ts):
    i = datetime.datetime.fromisoformat(ts)
    return i.isoformat()

def convert_severity(severity):
    if severity <= 0:
        return 'Unknown'
    if severity > 4:
        return 'High'
    return {1:'Info', 2:'Low', 3:'Medium', 4:'High'}[severity]

def fix_ip(ip):
    if ip == '':
        return '127.0.0.1'
    return ip

def fix_protocol(proto):
    if proto == '':
        return 'UNKNOWN'
    return proto

class SuricataConverter(JSONConverter):
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
        return ('event_type' in src
                and src['event_type'] == 'alert'
                and 'category' in src['alert']
                and src['alert']['category'] != 'Generic Protocol Command Decode')
