'''
The zoneminder to IDMEFv2 convertor.
'''
import re
import base64
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid

#
# The zoneminder converter takes as input a "flat" dictionary having
# - as keys the event tokens such as EN (name of the event) or ET (time of the event)
# - as values the values of the tokens
# Tokens are defined in:
# https://zoneminder.readthedocs.io/en/stable/userguide/filterevents.html
#

def _fix_zoneminder_date(zm_date: str) -> str:
    pat = r"([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2})"
    m = re.match(pat, zm_date)
    if m is None:
        return "1970-01-01T00:00:00"
    return m.group(1) + "T" + m.group(2)

def _make_description(d: str, m: str) -> str:
    return f"Event {d} on monitor {m}"

def _make_snapshot_base64(path: str) -> str:
    with open(path + "/snapshot.jpg", 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_output = base64_encoded_data.decode('ascii')
        return base64_output

# pylint: disable=too-few-public-methods
class ZoneminderConverter(JSONConverter):
    '''
    A class converting zoneminder event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (_fix_zoneminder_date, '$.ET'),
        'Category': ['Intrusion.Burglary'],
        'Priority': 'High',
        'Description' : (_make_description, '$.ED', "$.MN"),
        "Analyzer": {
            "IP": "127.0.0.1",
            "Name": "zoneminder",
            "Model": "Zoneminder video surveillance system",
            "Category": [
                "ODC"
            ],
            "Data": [
                "Images"
            ],
            "Method": [
                "Movement"
            ]
        },
        "Attachment": [
            {
                "Name": "EventFilePath",
                "FileName": "$.EFILE",
                "ContentType": "image/jpeg",
                "ContentEncoding": "base64",
                "Content": (_make_snapshot_base64, "$.EFILE")
            }
        ]
    }

    def __init__(self):
        super().__init__(ZoneminderConverter.IDMEFV2_TEMPLATE)
