"""
Data models for the Zabbix connector.

Defines classes for authentication, server info, and internal caching
to optimize API calls.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Set
from requests import Session

@dataclass
class ZabbixAuth:
    """
    Authentication data for the Zabbix API.
    """
    url: str
    user: str
    password: str

@dataclass
class ZabbixServerInfo:
    """
    Target Zabbix server information, including polling interval.
    """
    hostname: str
    ip: str
    port: int
    poll_interval: int = 30

@dataclass
class ZabbixCache:
    """
    Internal cache to map triggers to hosts, hosts to interfaces,
    and to keep track of seen event IDs.
    """
    trigger_host_map: Dict[str, str] = field(default_factory=dict)
    host_iface_map: Dict[str, Tuple[str, int]] = field(default_factory=dict)
    seen_eventids: Set[str] = field(default_factory=set)

@dataclass
class _ZabbixContext:
    """
    Internal context container for connection-related data.

    Groups together authentication credentials, HTTP session, server
    information, and the temporary authentication token used for interacting
    with the Zabbix API.
    """
    auth: ZabbixAuth
    session: Session
    token: str | None
    server_info: ZabbixServerInfo
