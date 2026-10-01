'''
The Kismet to IDMEFv2 convertor.
'''
import uuid
import datetime
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_my_local_ip

def convert_kismet_timestamp(ts):
    '''
    Convert Kismet timestamp (epoch) to IDMEFv2 format (ISO 8601)
    '''
    try:
        if isinstance(ts, (int, float)):
            return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()
        # Fallback if it's already a string, try to parse or return as is
        return str(ts)
    except Exception:  # pylint: disable=broad-exception-caught
        # Default to now if failed
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

def convert_severity(severity):
    '''
    Converts a Kismet severity to a IDMEFv2 severity
    Args:
        severity (int): the Kismet severity
    Returns:
        str: the IDMEFv2 severity, an enum in IDMEFv2 schema
    '''
    try:
        sev = int(severity)
        # Mapping Kismet severity (0-20 approx) to IDMEFv2
        if sev < 5:
            return 'Info'
        if sev < 10:
            return 'Low'
        if sev < 15:
            return 'Medium'
        return 'High'
    except (ValueError, TypeError):
        return 'Unknown'

def fix_mac(mac):
    '''
    Fix MAC if empty
    '''
    if not mac:
        return '00:00:00:00:00:00'
    return mac

# Kismet groups every alert definition into one of these classes
# (see activate_configured_alert() calls in Kismet's own source).
# Add new classes here as Kismet introduces them.
_CLASS_CATEGORY = {
    'PROBE': ['Recon.Network'],
    'DENIAL': ['Availability.DoS'],
    'SPOOF': ['Fraud.Masquerade'],
    'EXPLOIT': ['Access.Unauthorized'],
    'SYSTEM': ['Other.Undetermined'],
    'OTHER': ['Other.Undetermined'],
}

def map_category(alert_class):
    '''
    Maps the Kismet alert class to an IDMEFv2 category.
    '''
    return _CLASS_CATEGORY.get(str(alert_class).upper(), ['Other.Undetermined'])

class KismetConverter(JSONConverter):
    '''
    A class converting Kismet alerts to IDMEFv2 format.
    Inherits from JSONConverter.
    '''

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V08',
        'ID': lambda: str(uuid.uuid4()),
        'CreateTime': (convert_kismet_timestamp, '$."kismet.alert.timestamp"'),
        'Type': ['Cyber'],
        'Category': (map_category, '$."kismet.alert.class"'),
        'Priority': (convert_severity, '$."kismet.alert.severity"'),
        'Description' : '$."kismet.alert.text"',
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "kismet",
            "Model": "Kismet Wireless IDS",
            "Category": [
                "NET.NIDS", "NET.WIDS"
            ],
            "Data": [
                "Network"
            ],
            "Method": [
                "Monitor"
            ]
        },
        'Source': [
            {
                'ID': lambda: str(uuid.uuid4()),
                'Note': (lambda mac: f"MAC: {mac}", '$."kismet.alert.source_mac"'),
            },
        ],
    }

    def __init__(self):
        super().__init__(KismetConverter.IDMEFV2_TEMPLATE)

    def filter(self, _src: dict) -> bool:
        '''
        Filters out invalid alerts
        '''
        return True
