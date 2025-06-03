'''
The clamav to IDMEFv2 convertor.
'''
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid, idmefv2_convert_timestamp

# pylint: disable=too-few-public-methods
class ClamavConverter(JSONConverter):
    '''
    A class converting clamav metadata.json to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (idmefv2_convert_timestamp, '$.timestamp'),
        'Category': ['Recon.Scanning'],
        'Priority': 'High',
        'Description' : '$.alert.category',
        "Analyzer": {
            "IP": "127.0.0.1",
            "Name": "clamav",
            "Model": "Clamav Antivirus",
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
        # "Attachment": [
        #     {
        #         "Name": "syscheck",
        #         "FileName": "$.syscheck.path",
        #         "Hash": [
        #             (cat, "sha-1:", "$.syscheck.sha1_after"),
        #             (cat, "sha-256:", "$.syscheck.sha256_after"),
        #         ],
        #         "Size": (int, "$.syscheck.size_after"),
        #     },
        # ],
    }

    def __init__(self):
        super().__init__(ClamavConverter.IDMEFV2_TEMPLATE)

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
