'''
The zoneminder to IDMEFv2 convertor.
'''
from datetime import datetime
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid

#
# The zoneminder converter takes as input a "flat" dictionary having
# - as keys the event tokens such as EN (name of the event) or ET (time of the event)
# - as values the values of the tokens
# Tokens are defined in:
# https://zoneminder.readthedocs.io/en/stable/userguide/filterevents.html
#

def _create_time():
    return datetime.now().astimezone().isoformat()

# pylint: disable=too-few-public-methods
class ZoneminderConverter(JSONConverter):
    '''
    A class converting zoneminder event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': '$.ET',
        'Category': ['Intrusion.Burglary'],
        'Priority': 'High',
        'Description' : '$.ED',
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
    }

    def __init__(self):
        super().__init__(ZoneminderConverter.IDMEFV2_TEMPLATE)
