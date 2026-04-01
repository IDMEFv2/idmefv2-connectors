# pylint: disable=duplicate-code
'''
The motion to IDMEFv2 convertor.
'''
import re
import base64
from ..jsonconverter import JSONConverter, ChainJSONConverter
from ..idmefv2funs import idmefv2_uuid, idmefv2_my_local_ip, idmefv2_my_host_name

#
# The motion converter takes as input a "flat" dictionary having
# - as keys the event tokens such as EN (name of the event) or ET (time of the event)
# - as values the values of the tokens
# Tokens are defined in:
# https://motion-project.github.io/4.5.1/motion_config.html
#

def _fix_motion_date(motion_date: str) -> str:
    pat = r"([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2})"
    m = re.match(pat, motion_date)
    if m is None:
        return "1970-01-01T00:00:00"
    return m.group(1) + "T" + m.group(2)

def _make_description(d: str, m: str) -> str:
    return f"Event {d} on monitor {m}"

def _make_snapshot_base64(path: str) -> str:
    try:
        file_handle = open(path, 'rb')
    except FileNotFoundError:
        return ""
    with file_handle as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_output = base64_encoded_data.decode('ascii')
        return base64_output

def get_stream_uri(camera_id: str, stream_port: int) -> str:
    '''
    Get the stream URI for a given camera ID and stream port.
    The stream URI is in the format http://<ip>:<stream_port>/camera/<camera_id>
    '''
    ip = idmefv2_my_local_ip()
    return f"http://{ip}:{stream_port}/camera/{camera_id}"

# pylint: disable=too-few-public-methods
class MotionPictureSaveConverter(JSONConverter):
    '''
    A class converting motion event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V05',
        'ID': idmefv2_uuid,
        'CreateTime': (_fix_motion_date, '$.date'),
        'Category': ['Intrusion.Burglary'],
        'Priority': 'High',
        'Description' : (_make_description, '$.event_name', "$.camera_id"),
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "motion",
            "Model": "Motion video surveillance system",
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
        "Sensor": [
            {
                "IP": idmefv2_my_local_ip,
                "Name": "camera sensor",
            }
        ],
        "Attachment": [
            {
                "Name": "EventDirectoryPath",
                "FileName": "$.file"
            },
            {
                "Name": "EventSnapshotImage",
                "ContentType": "image/jpeg",
                "ContentEncoding": "base64",
                "Content": (_make_snapshot_base64, "$.file")
            }
        ]
    }

    def __init__(self):
        template = MotionPictureSaveConverter.IDMEFV2_TEMPLATE
        template['ID'] = (self._idmefv2_uuid, '$.event_id')
        super().__init__(template)

    def filter(self, src: dict) -> bool:
        return src.get('event_name') == "picture_save"

# pylint: disable=too-few-public-methods
class MotionCameraLostConverter(JSONConverter):
    '''
    A class converting motion event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V05',
        'ID': idmefv2_uuid,
        'CreateTime': (_fix_motion_date, '$.date'),
        'Category': ['Availability.Failure'],
        'Priority': 'High',
        'Description' : (_make_description, '$.event_name', "$.camera_id"),
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "motion",
            "Model": "Motion video surveillance system",
            "Category": [
                "ODC"
            ],
            "Method": [
                "Integrity"
            ]
        },
        "Sensor": [
            {
                "IP": idmefv2_my_local_ip,
                "Name": "camera sensor",
            }
        ],
        "Target": [
            {
                "ID": "$.camera_id",
                "Hostname": idmefv2_my_host_name,
                "IP": idmefv2_my_local_ip,
                "Service": "VideoStream"
            }
        ]
    }

    def __init__(self):
        template = self.IDMEFV2_TEMPLATE
        template['ID'] = (self._idmefv2_uuid, '$.event_id')
        super().__init__(template)

    def filter(self, src: dict) -> bool:
        return src.get('event_name') == "camera_lost"

# pylint: disable=too-few-public-methods
class MotionEventStartConverter(JSONConverter):
    '''
    A class converting motion event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V05',
        'ID': idmefv2_uuid,
        'CreateTime': (_fix_motion_date, '$.date'),
        'Category': ['Intrusion.Burglary'],
        'Priority': 'High',
        'Description' : (_make_description, '$.event_name', "$.camera_id"),
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "motion",
            "Model": "Motion video surveillance system",
            "Category": [
                "ODC"
            ],
            "Method": [
                "Movement"
            ]
        },
        "Sensor": [
            {
                "IP": idmefv2_my_local_ip,
                "Name": "camera sensor",
            }
        ],
        "Attachment": [
            {
                "Name": "StreamURI",
                "ExternalURI": [(get_stream_uri, "$.camera_id", "$.stream_port")]
            }
        ]
    }

    def __init__(self, stream_port: int):
        self._stream_port = stream_port
        template = self.IDMEFV2_TEMPLATE
        template['ID'] = (self._idmefv2_uuid, '$.event_id')
        template['Attachment'][0]['ExternalURI'] = [(get_stream_uri, "$.camera_id", stream_port)]
        super().__init__(template)

    def filter(self, src: dict) -> bool:
        return src.get('event_name') == "event_start"

# pylint: disable=too-few-public-methods
class MotionEventEndConverter(JSONConverter):
    '''
    A class converting motion event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V05',
        'ID': idmefv2_uuid,
        'CreateTime': (_fix_motion_date, '$.date'),
        'Category': ['Intrusion.Burglary'],
        'Priority': 'High',
        'Description' : (_make_description, '$.event_name', "$.camera_id"),
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "motion",
            "Model": "Motion video surveillance system",
            "Category": [
                "ODC"
            ],
            "Method": [
                "Movement"
            ]
        },
        "Sensor": [
            {
                "IP": idmefv2_my_local_ip,
                "Name": "camera sensor",
            }
        ],

    }

    def __init__(self):
        template = self.IDMEFV2_TEMPLATE
        template['ID'] = (self._idemfv2_uuid_terminate, '$.event_id')
        super().__init__(template)

    def filter(self, src: dict) -> bool:
        return src.get('event_name') == "event_end"

# pylint: disable=too-few-public-methods
class MotionMovieEndConverter(JSONConverter):
    '''
    A class converting motion event data to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V05',
        'ID': idmefv2_uuid,
        'CreateTime': (_fix_motion_date, '$.date'),
        'Category': ['Intrusion.Burglary'],
        'Priority': 'High',
        'Description' : (_make_description, '$.event_name', "$.camera_id"),
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "motion",
            "Model": "Motion video surveillance system",
            "Category": [
                "ODC"
            ],
            "Method": [
                "Movement"
            ]
        },
        "Sensor": [
            {
                "IP": idmefv2_my_local_ip,
                "Name": "camera sensor",
            }
        ],
        "Attachment": [
            {
                "Name": "EventRecordFilePath",
                "FileName": "$.file"
            }
        ]
    }

    def __init__(self):
        template = self.IDMEFV2_TEMPLATE
        template['ID'] = (self._idmefv2_uuid, '$.event_id')
        super().__init__(template)

    def filter(self, src: dict) -> bool:
        return src.get('event_name') == "movie_end"

class MotionConverter(ChainJSONConverter):
    '''
    A class converting motion event data to IDMEFv2 format.
    Inherits from ChainJSONConverter, as it is a chain of two converters:
        - MotionPictureSaveConverter, which converts motion event data to IDMEFv2 format
        - JSONConverter, which converts the output of MotionPictureSaveConverter to a JSON dict
    '''
