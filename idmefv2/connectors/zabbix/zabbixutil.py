"""
Utility functions for Zabbix connectors.

Includes:
- Host/IP resolution from Zabbix URL
- Common Zabbix API RPC call handler
- Host and trigger info retrieval with caching
- Persistence of the trigger-id -> last IDMEFv2 alert state (PredID chaining)
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
from typing import Any
from urllib.parse import urlparse

import requests

from .models import ZabbixCache, ZabbixServerInfo

log = logging.getLogger("zabbix-connector")

_ALERT_STATE_PATH = os.path.join(os.path.dirname(__file__), "zabbix_alert_state.json")
_alert_state_lock = threading.Lock()


def load_alert_state() -> dict[str, dict[str, Any]]:
    """
    Load the trigger-id -> last-sent IDMEFv2 alert map from disk.

    Used both to populate PredID (when a trigger fires again, the previous
    alert-id for that trigger marks the new alert as an update of the old
    one) and to let a "Closed" update inherit fields - such as Source/Target -
    that aren't available when converting the resolved problem itself.
    """
    with _alert_state_lock:
        if not os.path.exists(_ALERT_STATE_PATH):
            return {}
        try:
            with open(_ALERT_STATE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError) as e:
            log.error("Failed to load alert state: %s", e)
        return {}


def save_alert_state(state: dict[str, dict[str, Any]]) -> None:
    """Persist the trigger-id -> last-sent IDMEFv2 alert map atomically."""
    with _alert_state_lock:
        tmp_path = f"{_ALERT_STATE_PATH}.tmp"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, _ALERT_STATE_PATH)


def resolve_zabbix_server_info(url: str) -> ZabbixServerInfo:
    """
    Parse a Zabbix URL to determine hostname, IP, and port.

    Args:
        url (str): The Zabbix API base URL.

    Returns:
        ZabbixServerInfo: Dataclass with hostname, resolved IP, and port.
    """
    parsed = urlparse(url.rstrip("/"))
    host = parsed.hostname or "unknown"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        ip = host  # fallback to unresolved host
    return ZabbixServerInfo(hostname=host, ip=ip, port=port)


def perform_rpc(
    session: requests.Session,
    url: str, token: str | None,
    method: str,
    params: dict[str, Any] | None = None
) -> Any:
    """
    Perform a Zabbix JSON-RPC call and return the result or raise on error.

    Args:
        session (requests.Session): Active session object.
        url (str): Zabbix API endpoint.
        token (Optional[str]): Bearer token if authenticated.
        method (str): The Zabbix RPC method.
        params (dict, optional): Parameters for the method.

    Returns:
        Any: The result from the Zabbix API.

    Raises:
        RuntimeError: If Zabbix API returns an error.
        requests.HTTPError: If HTTP request fails.
    """
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {},
    }
    response = session.post(url, json=payload, headers=headers, timeout=5)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data["result"]


def get_hostid_for_trigger(
    session: requests.Session,
    url: str,
    token: str,
    trigger_id: str,
    cache: ZabbixCache,
) -> str:
    """
    Get host ID for a given trigger ID, with caching.

    Args:
        session (requests.Session): HTTP session.
        url (str): Zabbix API URL.
        token (str): Authentication token.
        trigger_id (str): Zabbix trigger ID.
        cache (ZabbixCache): Cache instance.

    Returns:
        str: Host ID
    """
    if trigger_id not in cache.trigger_host_map:
        result = perform_rpc(
            session,
            url,
            token,
            "trigger.get",
            {
                "triggerids": [trigger_id],
                "output": ["triggerid"],
                "selectHosts": ["hostid", "name"],
            },
        )
        host = result[0]["hosts"][0]
        cache.trigger_host_map[trigger_id] = host["hostid"]
        cache.trigger_host_map[f"name_{trigger_id}"] = host["name"]
    return cache.trigger_host_map[trigger_id]


def get_iface_for_host(
    session: requests.Session,
    url: str,
    token: str,
    host_id: str,
    cache: ZabbixCache,
) -> tuple[str, int]:
    """
    Get IP and port for the interface of a host, with caching.

    Args:
        session (requests.Session): HTTP session.
        url (str): Zabbix API URL.
        token (str): Authentication token.
        host_id (str): Host ID.
        cache (ZabbixCache): Cache instance.

    Returns:
        Tuple[str, int]: IP address and port number.
    """
    if host_id not in cache.host_iface_map:
        result = perform_rpc(
            session,
            url,
            token,
            "host.get",
            {
                "hostids": [host_id],
                "output": ["hostid"],
                "selectInterfaces": ["type", "ip", "dns", "port"],
            },
        )
        iface = next(
            (i for i in result[0]["interfaces"] if int(i["type"]) == 1),
            result[0]["interfaces"][0],
        )
        ip = iface["ip"] or iface["dns"]
        port = int(iface["port"])
        cache.host_iface_map[host_id] = (ip, port)
    return cache.host_iface_map[host_id]
