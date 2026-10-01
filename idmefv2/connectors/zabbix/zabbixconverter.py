"""
Translate a Zabbix “problem” object into a fully compliant IDMEFv2 message,
with configurable Analyzer.Method from runtime parameters.
"""

from __future__ import annotations

import datetime as _dt
import uuid as _uuid
from typing import Any, Mapping, Sequence

from ..jsonconverter import JSONConverter
from ..idmefv2funs import idmefv2_my_local_ip


def _idmef_uuid() -> str:
    """Return a new UUIDv4 as a plain string."""
    return _uuid.uuid4().urn[9:]


def _iso_timestamp(epoch: str | int) -> str:
    """Convert epoch seconds to ISO‑8601 with UTC timezone."""
    return _dt.datetime.fromtimestamp(int(epoch), tz=_dt.timezone.utc).isoformat()


def _severity(sev: int | str) -> str:
    """Map Zabbix severity (0…5) to IDMEFv2 priority."""
    return {
        0: "Unknown",
        1: "Info",
        2: "Low",
        3: "Medium",
        4: "High",
        5: "High",  # Zabbix "Disaster": priorityEnum has no "Critical" value
    }.get(int(sev), "Unknown")


def _map_category(name: str) -> list[str]:
    """Choose IDMEFv2 Category based on trigger name."""
    n = name.lower()
    if "unreachable" in n or "down" in n:
        return ["Availability.Outage"]
    if "load" in n or "cpu" in n:
        return ["Availability.Failure"]
    return ["Other.Undetermined"]


def _listify_port(port: Any) -> list[int]:
    """Wrap port as a one‑element int list if valid, else return empty list."""
    try:
        return [int(port)]
    except (TypeError, ValueError):
        return []


def _format_pred_id(pred_id: str | None) -> list[str]:
    """Wrap the predecessor alert-id as a one-element list, or empty if none."""
    return [pred_id] if pred_id else []


class ZabbixConverter(JSONConverter):
    """Convert a Zabbix problem dict into an IDMEFv2 message with dynamic "Analyzer.Method"."""

    def __init__(self, analyzer_methods: Sequence[str] | None = None) -> None:
        # Default to ['Monitor', 'Threshold'] if not provided
        if analyzer_methods:
            methods = []
            for m in analyzer_methods:
                if m.lower() in ('polling', 'push'):
                    # Map internal modes to valid IDMEFv2 Analyzer.Method enum
                    if 'Monitor' not in methods:
                        methods.append('Monitor')
                else:
                    methods.append(m)
        else:
            methods = ['Monitor', 'Threshold']

        template: Mapping[str, Any] = {
            'Version': '2.D.V08',
            'ID': _idmef_uuid,
            'CreateTime': (_iso_timestamp, '$.clock'),
            'Type': ['Availability'],
            'Status': ['Open'],
            'Category': (_map_category, '$.name'),
            'Priority': (_severity, '$.severity'),
            'Description': '$.name',
            'PredID': (_format_pred_id, '$.pred_id'),
            'Analyzer': {
                'IP': idmefv2_my_local_ip,
                'Name': 'zabbix',
                'Model': 'Zabbix Monitoring',
                'Category': ['SIEM.NMS'],
                'Data': ['Data'],
                'Method': methods,
            },
            'Source': [
                {
                    'ID': _idmef_uuid,
                    'Hostname': '$.hosts[0].name',
                    'IP': '$.extra.ip',
                    'Port': (_listify_port, '$.extra.port'),
                }
            ],
            'Target': [
                {
                    'ID': _idmef_uuid,
                    'Hostname': '$.extra_target.hostname',
                    'IP': '$.extra_target.ip',
                    'Port': (_listify_port, '$.extra_target.port'),
                }
            ],
        }
        super().__init__(template)

    def filter(self, src: dict[str, Any]) -> bool:
        """
        Discard events that are missing required fields:
        - 'clock'
        - 'severity'
        """
        return ('clock' in src) and ('severity' in src)


class ZabbixCloseConverter(JSONConverter):
    """
    Convert a resolved Zabbix problem into an IDMEFv2 "closed" update,
    chained to the original alert via PredID. The resolved problem itself
    carries no Source/Target/host info, so those are inherited from the
    previous alert sent for this trigger (see poller.py/push.py).
    """

    def __init__(self) -> None:
        template: Mapping[str, Any] = {
            'Version': '2.D.V08',
            'ID': _idmef_uuid,
            'CreateTime': (_iso_timestamp, '$.clock'),
            'Type': ['Availability'],
            'Status': ['Closed'],
            'Category': (_map_category, '$.name'),
            'Priority': (_severity, '$.severity'),
            'Description': '$.name',
            'PredID': (_format_pred_id, '$.pred_id'),
            'Analyzer': {
                'IP': idmefv2_my_local_ip,
                'Name': 'zabbix',
                'Model': 'Zabbix Monitoring',
                'Category': ['SIEM.NMS'],
                'Data': ['Data'],
                'Method': ['Monitor'],
            },
            'Source': '$.source',
            'Target': '$.target',
        }
        super().__init__(template)

    def filter(self, src: dict[str, Any]) -> bool:
        """Discard events that are missing required fields: 'clock', 'severity'."""
        return ('clock' in src) and ('severity' in src)
