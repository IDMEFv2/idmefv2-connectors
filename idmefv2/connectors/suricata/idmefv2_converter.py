import uuid
from ..jsonconverter import JSONConverter

def idmefv2_uuid():
    return uuid.uuid4().urn[9:]

class IDMEFv2Converter(JSONConverter):
    IDMEFV2_TEMPLATE = {
        'Version': '2.0.3',
        'ID': idmefv2_uuid,
        'CreateTime': '$.timestamp',
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
        'Source': {
            'IP': '$.src_ip',
            'Port': '$.src_port',
            'Protocol': '$.proto',
        },
        'Target': {
            'IP': '$.dest_ip',
            'Port': '$.dest_port',
        },
    }

    def __init__(self):
        super().__init__(IDMEFv2Converter.IDMEFV2_TEMPLATE)
