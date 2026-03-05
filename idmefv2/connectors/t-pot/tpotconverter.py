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

class TpotConverter(JSONConverter):
    """
    T-Pot to IDMEFv2 Converter.
    Updated to match official Logstash T-Pot mapping.
    """

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (_convert_timestamp, '$.@timestamp'),
        'Description': (_generate_description, '$'),
        'Priority': 'Medium',
        'Category': ['Attempt.Login'],
        'Analyzer': {
            'IP': idmefv2_my_local_ip,
            'Name': (lambda x: f"tpot-{x.lower()}" if x else "tpot-unknown", '$.type'), 
            'Type': ['Cyber'],
            'Method': ['Honeypot']
        },
        'Source': [
            {
                'IP': '$.src_ip',
                'Port': (lambda x: [int(x)] if x else [], '$.src_port'),
            },
        ],
        'Target': [
            {
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
        CRITICAL FILTER:
        Ensures compliance with official T-Pot field naming (dest_ip).
        """
        # Changed 'dst_ip' to 'dest_ip' to match official mapping output
        required = ['src_ip', 'dest_ip', 'type', '@timestamp']

        return all(src.get(field) is not None for field in required)
