"""
The T-Pot to IDMEFv2 converter.
"""
from __future__ import annotations
import datetime
from typing import Any
from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid, idmefv2_my_local_ip

def _convert_timestamp(timestamp_str: str | None) -> str:
    """Safe timestamp conversion with fallback."""
    if not timestamp_str:
        return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        parsed = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return parsed.strftime('%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, AttributeError):
        return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def _generate_description(src: Any) -> str:
    """Generates a human-readable description based on the sensor type and event details."""
    if not isinstance(src, dict):
        return "T-Pot: Honeypot activity detected"

    # Official T-Pot mapping uses capitalized names (e.g., 'Cowrie')
    sensor_type = src.get('type', 'unknown').lower()
    description = f"T-Pot: Activity detected on {src.get('type', 'unknown')} sensor"

    if sensor_type == 'cowrie':
        if src.get('message'):
            description = f"Cowrie: {src['message']}"
        else:
            eventid = src.get('eventid', '')
            if 'login.failed' in eventid:
                description = f"Cowrie: Failed login attempt (user: {src.get('username', 'N/A')})"
            elif 'session.connect' in eventid:
                description = "Cowrie: New SSH/Telnet connection"
            else:
                description = "Cowrie: Remote interaction detected"

    if sensor_type == "dionaea":
        conn_info = src.get('connection', {})
        proto = str(conn_info.get('protocol', 'unknown')).upper()

        user = src.get('username', 'none')
        pwd = src.get('password', 'none')

        description = f"Dionaea: {proto} login attempt with user '{user}'"
        if pwd != 'none':
            description += f" and password '{pwd}'"

    elif sensor_type == 'honeytrap':
        description = f"Honeytrap: Connection on port {src.get('dest_port', 'unknown')}"

    return description

# Cowrie and Dionaea capture actual (attempted) authentication, so they are
# reported as unauthorized access attempts. Honeytrap only observes bare
# TCP/UDP connections with no credentials involved, which is reconnaissance
# rather than an access attempt. Add new sensors here as they are supported.
_SENSOR_CATEGORY = {
    'cowrie': ['Access.Unauthorized'],
    'dionaea': ['Access.Unauthorized'],
    'honeytrap': ['Recon.Network'],
}

def _map_category(sensor_type: str | None) -> list[str]:
    """Maps the T-Pot sensor type to an IDMEFv2 category."""
    return _SENSOR_CATEGORY.get(str(sensor_type).lower(), ['Other.Undetermined'])

class TpotConverter(JSONConverter):
    """
    T-Pot to IDMEFv2 Converter.
    Updated to match official Logstash T-Pot mapping.
    """

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V08',
        'ID': idmefv2_uuid,
        'CreateTime': (_convert_timestamp, '$.@timestamp'),
        'Description': (_generate_description, '$'),
        'Priority': 'Medium',
        'Type': ['Cyber'],
        'Category': (_map_category, '$.type'),
        'Analyzer': {
            'IP': idmefv2_my_local_ip,
            'Name': (lambda x: f"tpot-{x.lower()}" if x else "tpot-unknown", '$.type'),
            'Method': ['Honeypot']
        },
        'Source': [
            {
                'ID': idmefv2_uuid,
                'IP': '$.src_ip',
                'Port': (lambda x: [int(x)] if x else [], '$.src_port'),
            },
        ],
        'Target': [
            {
                'ID': idmefv2_uuid,
                # Field changed from dst_ip to dest_ip to match logstash.conf rename
                'IP': '$.dest_ip',
                'Port': (lambda x: [int(x)] if x else [], '$.dest_port'),
            },
        ],
    }

    def __init__(self):
        super().__init__(TpotConverter.IDMEFV2_TEMPLATE)

    def filter(self, src: dict[str, Any]) -> bool:
        """
        Discards events missing required fields. A truthy check (not just
        "is not None") is required because some T-Pot events (e.g. Dionaea's
        internal "listen" events) carry an empty-string src_ip with no real
        peer, which would otherwise fail IP format validation downstream.
        """
        required = ['src_ip', 'dest_ip', 'type', '@timestamp']

        return all(src.get(field) for field in required)
