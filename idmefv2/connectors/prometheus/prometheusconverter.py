"""
Translate a Prometheus alert object into a fully compliant IDMEFv2 message.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Mapping

from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_uuid, idmefv2_my_local_ip


def _convert_timestamp(timestamp_str: str) -> str:
    """
    Convert Prometheus activeAt timestamp to IDMEFv2 format.

    Args:
        timestamp_str: Timestamp in ISO 8601 format from Prometheus.

    Returns:
        str: Timestamp in IDMEFv2 format.
    """
    # Prometheus uses ISO 8601 format like "2018-07-04T20:27:12.60602144+02:00"
    # We need to parse and re-format it
    try:
        # Handle microseconds with more than 6 digits by truncating
        if '.' in timestamp_str:
            base, frac_and_tz = timestamp_str.split('.', 1)
            # Find where the timezone starts (+ or - after the decimal)
            tz_pos = -1
            for i, char in enumerate(frac_and_tz):
                if char in ('+', '-') and i > 0:
                    tz_pos = i
                    break
                if char == 'Z':
                    tz_pos = i
                    break

            if tz_pos > 0:
                frac = frac_and_tz[:tz_pos][:6]  # Truncate to 6 digits
                tz_part = frac_and_tz[tz_pos:]
                timestamp_str = f"{base}.{frac}{tz_part}"

        parsed = _dt.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return parsed.isoformat()
    except (ValueError, AttributeError):
        # If parsing fails, return current time
        return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _convert_severity(severity: str) -> str:
    """
    Map Prometheus severity label to IDMEFv2 priority.

    Args:
        severity: Prometheus severity label value.

    Returns:
        str: IDMEFv2 priority string.
    """
    severity_lower = str(severity).lower()
    mapping = {
        'critical': 'High',
        'high': 'High',
        'warning': 'Medium',
        'medium': 'Medium',
        'low': 'Low',
        'info': 'Info',
        'information': 'Info',
        'none': 'Unknown',
    }
    return mapping.get(severity_lower, 'Unknown')


def _extract_hostname(instance: str) -> str:
    """
    Extract hostname from Prometheus instance label.

    Args:
        instance: Instance label value (e.g., "host:9090" or "192.168.1.1:9090").

    Returns:
        str: Hostname or IP without port.
    """
    if not instance:
        return 'unknown'
    # Remove port if present
    if ':' in instance:
        # Handle IPv6 addresses
        if instance.startswith('['):
            # IPv6 format: [::1]:9090
            bracket_end = instance.find(']')
            if bracket_end > 0:
                return instance[1:bracket_end]
        else:
            # IPv4 or hostname: host:9090
            return instance.rsplit(':', 1)[0]
    return instance


def _map_category(alertname: str) -> list[str]:
    """
    Map alert name to IDMEFv2 category.

    Args:
        alertname: The Prometheus alert name.

    Returns:
        list[str]: List of IDMEFv2 categories.
    """
    name_lower = alertname.lower()
    if 'down' in name_lower or 'unreachable' in name_lower:
        return ['Availability.Outage']
    if 'high' in name_lower and ('cpu' in name_lower or 'memory' in name_lower):
        return ['Availability.Failure']
    if 'disk' in name_lower or 'storage' in name_lower:
        return ['Availability.Failure']
    if 'latency' in name_lower or 'slow' in name_lower:
        return ['Availability.Failure']
    return ['Other.Uncategorised']


# pylint: disable=too-few-public-methods
class PrometheusConverter(JSONConverter):
    """
    Convert a Prometheus alert dict into an IDMEFv2 message.

    Inherits from JSONConverter and defines the template mapping
    from Prometheus alert format to IDMEFv2 format.
    """

    def __init__(self) -> None:
        """Initialize the converter with the IDMEFv2 template."""
        template: Mapping[str, Any] = {
            'Version': '2.D.V04',
            'ID': idmefv2_uuid,
            'CreateTime': (_convert_timestamp, '$.activeAt'),
            'Category': (_map_category, '$.labels.alertname'),
            'Priority': (_convert_severity, '$.labels.severity'),
            'Description': '$.labels.alertname',
            'Analyzer': {
                'IP': idmefv2_my_local_ip,
                'Name': 'prometheus',
                'Model': 'Prometheus Monitoring',
                'Type': 'Monitor',
                'Category': ['NMS'],
                'Data': ['System'],
                'Method': ['Polling'],
            },
            'Source': [
                {
                    'Hostname': (_extract_hostname, '$.labels.instance'),
                },
            ],
        }
        super().__init__(template)

    def filter(self, src: dict[str, Any]) -> bool:
        """
        Filter Prometheus alerts that should be converted.

        Only convert alerts that are in 'firing' state.

        Args:
            src: The Prometheus alert dict.

        Returns:
            bool: True if the alert should be converted.
        """
        return src.get('state', '').lower() == 'firing'
