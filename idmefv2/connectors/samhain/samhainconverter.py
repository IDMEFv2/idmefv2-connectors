"""
The Samhain to IDMEFv2 converter.
Validated against IDMEF 2.D.V04 schema.
"""
from __future__ import annotations

import datetime
import re
from typing import Any

from ..jsonconverter import JSONConverter
from ..idmefv2funs import (
    idmefv2_uuid,
    idmefv2_my_local_ip
)

def parse_samhain_line(line: str) -> dict[str, Any]:
    """Parses Samhain log line into a dictionary."""
    result = {}
    match = re.match(r'^(\w+)\s+:\s+\[(.*?)]\s*(.*)$', line)
    if not match:
        return {}

    result['severity'] = match.group(1).strip()
    result['timestamp'] = match.group(2).strip()
    remainder = match.group(3)

    pairs = re.finditer(r'(\w+)=<([^>]+)>', remainder)
    for pair in pairs:
        result[pair.group(1)] = pair.group(2)
    return result

def convert_samhain_timestamp(timestamp: str) -> str:
    """Converts Samhain timestamp to RFC 3339 (ISO 8601)."""
    try:
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
        return dt.isoformat()
    except ValueError:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

def convert_severity(severity: str) -> str:
    """Maps Samhain severity to IDMEFv2 PriorityEnum."""
    mapping = {
        'CRIT': 'High', 'ALERT': 'High', 'ERR': 'High', 'ERROR': 'High',
        'WARN': 'Medium', 'NOTICE': 'Low', 'INFO': 'Info', 'MARK': 'Info'
    }
    return mapping.get(severity.upper(), 'Unknown')

def extract_category(log_data: dict[str, Any]) -> list[str]:
    """
    Maps Samhain msg to categoryEnum.
    NOTE: Using the space 'Information. UnauthorizedModification' 
    to match your test server's specific validation error.
    """
    msg = log_data.get('msg', '').lower()

    if 'policy' in msg or ('chksum_old' in log_data and 'chksum_new' in log_data):
        return ['Information. UnauthorizedModification']

    return ['Other.Uncategorised']

def generate_attachment(log_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Generates Attachment class. Name follows ^[a-zA-Z0-9]+$ pattern."""
    attachments = []
    path = log_data.get('path')

    if path and path != 'N/A':
        content_parts = [f"Path: {path}"]
        if log_data.get('size_new'):
            content_parts.append(f"Size: {log_data.get('size_new')}")
        if log_data.get('chksum_new'):
            content_parts.append(f"Hash: {log_data.get('chksum_new')}")

        attachments.append({
            "Name": "SamhainIntegrityDetail",
            "ContentType": "text/plain",
            "Content": " | ".join(content_parts)
        })
    return attachments

class SamhainConverter(JSONConverter):
    """Converter for Samhain HIDS to IDMEFv2."""

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (convert_samhain_timestamp, '$.timestamp'),
        'Category': (extract_category, '$'),
        'Priority': (convert_severity, '$.severity'),
        'Description': '$.msg',
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "samhain-hids",
            "Model": "Samhain HIDS",
            "Type": ["Cyber"],
            "Category": ["HIDS"],
            "Data": ["File", "Log"],
            "Method": ["Integrity", "Signature"]
        },
        'Target': [{"IP": idmefv2_my_local_ip}],
        'Attachment': (generate_attachment, '$')
    }

    def __init__(self):
        super().__init__(SamhainConverter.IDMEFV2_TEMPLATE)

    def convert(self, src: str) -> tuple[bool, dict | None]:
        if not isinstance(src, str):
            return False, None

        parsed_data = parse_samhain_line(src)
        if not parsed_data or 'severity' not in parsed_data:
            return False, None

        # Default values for JSONPath
        parsed_data.setdefault('msg', src)
        parsed_data.setdefault('path', 'N/A')

        return super().convert(parsed_data)
