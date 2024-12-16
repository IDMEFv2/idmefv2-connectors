import datetime
import uuid
from idmefv2.connectors.jsonconverter import JSONConverter

def idmefv2_uuid():
    return uuid.uuid4().urn[9:]

def convert_timestamp(ts):
     i = datetime.datetime.fromisoformat(ts)
     return i.isoformat()

class SuricataConverter(JSONConverter):
    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (convert_timestamp, '$.timestamp'),
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
                'IP': '$.src_ip',
                'Port': [
                    '$.src_port',
                ],
                'Protocol': [
                    '$.proto',
                ],
            },
        ],
        'Target': [
            {
                'IP': '$.dest_ip',
                'Port': [
                    '$.dest_port',
                ],
            },
        ],
    }

    def __init__(self):
        super().__init__(SuricataConverter.IDMEFV2_TEMPLATE)
