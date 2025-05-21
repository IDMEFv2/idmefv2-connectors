"""
Module providing classes to handle incoming Zabbix push alerts.

Includes a helper class to interact with the Zabbix API for fetching
trigger and host information, and an HTTP handler class to process
push notifications, enrich them with additional data, convert them
using a converter, and forward them to an IDMEFv2 client.
"""

from __future__ import annotations
import json
import logging
from http.server import BaseHTTPRequestHandler
from typing import Any, Optional

import requests

from .zabbixconverter import ZabbixConverter
from ..idmefv2client import IDMEFv2Client
from .models import ZabbixAuth, ZabbixCache, ZabbixServerInfo
from .zabbixutil import (
    resolve_zabbix_server_info,
    perform_rpc,
    get_hostid_for_trigger,
    get_iface_for_host,
)

log = logging.getLogger("zabbix-connector")

# pylint: disable=too-few-public-methods
class ZabbixPushHelper:
    """
    Helper to fetch trigger/host details on demand from the Zabbix API.
    Used in push-mode to enrich incoming alerts.
    """

    def __init__(self, *, auth: ZabbixAuth) -> None:
        """
        Initialize the helper with ZabbixAuth dataclass containing URL and credentials.
        """
        self.auth = auth
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.cache = ZabbixCache()
        self.server_info = resolve_zabbix_server_info(self.auth.url)

    def login(self) -> None:
        """Obtain a bearer token from the Zabbix API."""
        payload = {
            "jsonrpc": "2.0", "id": 1,
            "method": "user.login",
            "params": {"username": self.auth.user, "password": self.auth.password}
        }
        r = self.session.post(self.auth.url, json=payload, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        self.token = data["result"]
        log.info("Authenticated to Zabbix API (token %s\u2026)", self.token[:8])


class PushHandler(BaseHTTPRequestHandler):
    """
    HTTP handler for incoming Zabbix push alerts.
    Expects POST /alert with Zabbix JSON; enriches via ZabbixPushHelper, converts
    via ZabbixConverter, then forwards to IDMEFv2Client.
    """
    converter: ZabbixConverter
    client: IDMEFv2Client
    helper: ZabbixPushHelper
    server_info: dict[str, Any]

    def log_message(self, *_args, **_kwargs) -> None:
        # disable base class logging
        return

    # pylint: disable=invalid-name
    def do_POST(self) -> None:
        """Handle POST requests sent to /alert endpoint."""
        if self.path != "/alert":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            src = json.loads(body)
        except json.JSONDecodeError as exc:
            log.error("Invalid JSON in push: %s", exc)
            self.send_error(400, "Bad Request – invalid JSON")
            return

        log.debug("Received push JSON: %s", src)

        try:
            # 1) fetch problem clock
            eid = str(src.get("eventid", ""))
            if not eid:
                raise ValueError("Missing eventid field")

            prob = perform_rpc(
                self.helper.session,
                self.helper.auth.url,
                self.helper.token,
                "problem.get",
                {"eventids": [eid], "output": ["clock"]},
            )
            if not prob:
                raise RuntimeError(f"eventid {eid} not found")
            src["clock"] = prob[0]["clock"]

            # 2) fetch host/interface details
            tid = perform_rpc(
                self.helper.session,
                self.helper.auth.url,
                self.helper.token,
                "problem.get",
                {"eventids": [eid], "output": ["objectid"]},
            )[0]["objectid"]

            hid = get_hostid_for_trigger(
                self.helper.session,
                self.helper.auth.url,
                self.helper.token,
                tid,
                self.helper.cache,
            )
            ip, port = get_iface_for_host(
                self.helper.session,
                self.helper.auth.url,
                self.helper.token,
                hid,
                self.helper.cache,
            )
            host_name = self.helper.cache.trigger_host_map.get(f"name_{tid}", "unknown")

            # 3) fetch trigger description & severity
            trg = perform_rpc(
                self.helper.session,
                self.helper.auth.url,
                self.helper.token,
                "trigger.get",
                {"triggerids": [tid], "output": ["description", "priority"]},
            )[0]
            src["name"] = trg.get("description", src.get("name", ""))
            src["severity"] = str(trg.get("priority", src.get("severity", "0")))

            # 4) fill any missing fields
            src.setdefault("hosts", [{"name": host_name}])
            src.setdefault("extra", {"ip": ip, "port": port})
            src.setdefault("extra", {})
            src['extra']['ip'] = ip or '0.0.0.0'
            src['extra']['port'] = port or 0

            if isinstance(self.helper.server_info, ZabbixServerInfo):
                src["extra_target"] = {
                    "hostname": self.helper.server_info.hostname,
                    "ip": self.helper.server_info.ip,
                    "port": self.helper.server_info.port,
                }
            else:
                src["extra_target"] = self.helper.server_info
                src['extra_target'].setdefault('hostname', 'unknown_target_hostname')
                src['extra_target'].setdefault('ip', '0.0.0.0')
                src['extra_target'].setdefault('port', 0)

            ok, msg = self.converter.convert(src)
            if ok:
                self.client.post(msg)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        # pylint: disable=broad-exception-caught
        except Exception as exc:
            log.exception("Push-handler error")
            self.send_error(500, f"Internal Server Error: {exc}")
