"""
The ModSecurity to IDMEFv2 converter.
"""
from __future__ import annotations

import datetime
from typing import Any
from ..jsonconverter import JSONConverter
from ..idmefv2funs import (
    idmefv2_uuid,
    idmefv2_my_local_ip
)


def convert_modsecurity_timestamp(timestamp: str) -> str:
    """
    Convert ModSecurity timestamp to ISO 8601 format.
    
    ModSecurity uses format: "Mon Feb  2 12:40:01 2026"
    
    Args:
        timestamp: ModSecurity timestamp string
    
    Returns:
        ISO 8601 formatted timestamp string
    """
    try:
        # Parse ModSecurity timestamp format: "Mon Feb  2 12:40:01 2026"
        # Note: handles both single and double-digit days
        dt = datetime.datetime.strptime(timestamp.strip(), "%a %b %d %H:%M:%S %Y")
        return dt.isoformat()
    except (ValueError, AttributeError):
        # Fallback: return current time if parsing fails
        return datetime.datetime.now().isoformat()



def convert_severity(severity: str | int) -> str:
    """
    Convert ModSecurity severity to IDMEFv2 Priority.
    
    ModSecurity uses numeric severity levels (0-7):
    - 0 = EMERGENCY
    - 1 = ALERT
    - 2 = CRITICAL
    - 3 = ERROR
    - 4 = WARNING
    - 5 = NOTICE
    - 6 = INFO
    - 7 = DEBUG

    Args:
        severity: ModSecurity severity level (numeric 0-7 or string)

    Returns:
        IDMEFv2 Priority enum value (High, Medium, Low, Info)
    """
    # Handle numeric severity (0-7)
    if isinstance(severity, int) or (isinstance(severity, str) and severity.isdigit()):
        severity_num = int(severity)
        numeric_mapping = {
            0: 'High',    # EMERGENCY
            1: 'High',    # ALERT
            2: 'High',    # CRITICAL
            3: 'High',    # ERROR
            4: 'Medium',  # WARNING
            5: 'Low',     # NOTICE
            6: 'Info',    # INFO
            7: 'Info',    # DEBUG
        }
        return numeric_mapping.get(severity_num, 'Unknown')

    # Handle string severity (fallback for compatibility)
    severity_lower = str(severity).lower()
    string_mapping = {
        'emergency': 'High',
        'alert': 'High',
        'critical': 'High',
        'error': 'High',
        'warning': 'Medium',
        'notice': 'Low',
        'info': 'Info',
        'debug': 'Info',
    }
    return string_mapping.get(severity_lower, 'Unknown')


def map_category(tags: list[str]) -> list[str]:
    # pylint: disable=too-many-return-statements
    """
    Map ModSecurity attack tags to IDMEFv2 Categories.

    Args:
        tags: List of ModSecurity tags from rule

    Returns:
        List of IDMEFv2 category strings
    """
    if not tags:
        return ['Other.Uncategorised']

    # Check for specific attack types
    # ModSecurity detects attack attempts, so we use Attempt.Exploit
    for tag in tags:
        tag_lower = tag.lower()
        if 'attack-sqli' in tag_lower or 'sql' in tag_lower:
            return ['Attempt.Exploit']
        if 'attack-xss' in tag_lower or 'xss' in tag_lower:
            return ['Attempt.Exploit']
        if 'attack-rce' in tag_lower or 'rce' in tag_lower:
            return ['Attempt.Exploit']
        if 'attack-lfi' in tag_lower or 'attack-rfi' in tag_lower:
            return ['Attempt.Exploit']
        if 'attack-injection' in tag_lower:
            return ['Attempt.Exploit']
        if 'protocol-violation' in tag_lower or 'protocol' in tag_lower:
            return ['Attempt.Exploit']

    return ['Other.Uncategorised']


def extract_client_ip(transaction: dict[str, Any]) -> str:
    """
    Extract client IP from transaction.

    Args:
        transaction: ModSecurity transaction object

    Returns:
        Client IP address or '0.0.0.0' if not found
    """
    return transaction.get('client_ip', '0.0.0.0')


def extract_host_ip(transaction: dict[str, Any]) -> str:
    """
    Extract host IP from transaction.

    Args:
        transaction: ModSecurity transaction object

    Returns:
        Host IP address or '0.0.0.0' if not found
    """
    return transaction.get('host_ip', '0.0.0.0')


def extract_request_uri(transaction: dict[str, Any]) -> str:
    """
    Extract request URI from transaction.

    Args:
        transaction: ModSecurity transaction object

    Returns:
        Request URI or empty string if not found
    """
    request = transaction.get('request', {})
    return request.get('uri', '')


def extract_message(messages: list[dict[str, Any]]) -> str:
    """
    Extract primary message from messages array.

    Args:
        messages: List of ModSecurity message objects

    Returns:
        First message text or 'Unknown' if not found
    """
    if not messages or len(messages) == 0:
        return 'Unknown'
    return messages[0].get('message', 'Unknown')


def extract_severity(messages: list[dict[str, Any]]) -> str:
    """
    Extract severity from first message.

    Args:
        messages: List of ModSecurity message objects

    Returns:
        Severity string for conversion
    """
    if not messages or len(messages) == 0:
        return 'UNKNOWN'
    details = messages[0].get('details', {})
    return details.get('severity', 'UNKNOWN')


def extract_tags(messages: list[dict[str, Any]]) -> list[str]:
    """
    Extract tags from first message.

    Args:
        messages: List of ModSecurity message objects

    Returns:
        List of tags or empty list
    """
    if not messages or len(messages) == 0:
        return []
    details = messages[0].get('details', {})
    return details.get('tags', [])


# pylint: disable=too-few-public-methods
class ModSecurityConverter(JSONConverter):
    """
    A class converting ModSecurity JSON audit logs to IDMEFv2 format.
    Inherits from JSONConverter.
    """

    IDMEFV2_TEMPLATE = {
        'Version': '2.D.V04',
        'ID': idmefv2_uuid,
        'CreateTime': (convert_modsecurity_timestamp, '$.transaction.time_stamp'),
        'Category': (map_category, (extract_tags, '$.transaction.messages')),
        'Priority': (convert_severity, (extract_severity, '$.transaction.messages')),
        'Description': (extract_message, '$.transaction.messages'),
        "Analyzer": {
            "IP": idmefv2_my_local_ip,
            "Name": "modsecurity",
            "Model": "ModSecurity WAF",
            "Type": "Cyber",
            "Category": [
                "WAF"
            ],
            "Data": [
                "Application"
            ],
            "Method": [
                "Signature"
            ]
        },
        'Source': [
            {
                'IP': (extract_client_ip, '$.transaction'),
            },
        ],
        'Target': [
            {
                'IP': (extract_host_ip, '$.transaction'),
                'URL': (extract_request_uri, '$.transaction'),
            },
        ],
    }

    def __init__(self):
        super().__init__(ModSecurityConverter.IDMEFV2_TEMPLATE)

    def filter(self, src: dict) -> bool:
        """
        Filter ModSecurity log entries.

        Args:
            src: The ModSecurity log entry

        Returns:
            True if entry should be converted, False otherwise
        """
        # Only process entries that have transaction and messages
        transaction = src.get('transaction', {})
        return ('transaction' in src
                and 'messages' in transaction
                and len(transaction['messages']) > 0)
