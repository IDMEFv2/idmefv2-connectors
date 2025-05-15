from __future__ import annotations
import json
import logging
import socket
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse

import requests

from .zabbixconverter import ZabbixConverter
from ..idmefv2client import IDMEFv2Client

log = logging.getLogger("zabbix-connector")


class ZabbixPushHelper:
    """
    Helper to fetch trigger/host details on demand from the Zabbix API.
    Used in push-mode to enrich incoming alerts.
    """

    def __init__(self, *, url: str, user: str, password: str) -> None:
        self.url      = url.rstrip("/")
        self.user     = user
        self.password = password

        self.session = requests.Session()
        self.token: str | None = None

        self.trigger_host_map: dict[str, str] = {}
        self.host_iface_map:   dict[str, tuple[str, int]] = {}

        parsed = urlparse(self.url)
        host = parsed.hostname or "unknown"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            ip = host
        self.server_info = {"hostname": host, "ip": ip, "port": port}

    def login(self) -> None:
        """Obtain a bearer token from the Zabbix API."""
        payload = {
            "jsonrpc": "2.0", "id": 1,
            "method": "user.login",
            "params": {"username": self.user, "password": self.password}
        }
        r = self.session.post(self.url, json=payload, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        self.token = data["result"]
        log.info("Authenticated to Zabbix API (token %s…)", self.token[:8])

    def _rpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Internal RPC wrapper for Zabbix API calls."""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        r = self.session.post(self.url, json=payload, headers=headers, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        return data["result"]

    def _get_hostid_for_trigger(self, trigger_id: str) -> str:
        """Cache and return host ID for a given trigger ID."""
        if trigger_id not in self.trigger_host_map:
            res = self._rpc(
                "trigger.get",
                {"triggerids": [trigger_id], "output": ["triggerid"], "selectHosts": ["hostid", "name"]}
            )
            host = res[0]["hosts"][0]
            self.trigger_host_map[trigger_id] = host["hostid"]
            self.trigger_host_map[f"name_{trigger_id}"] = host["name"]
        return self.trigger_host_map[trigger_id]

    def _get_iface_for_host(self, host_id: str) -> tuple[str, int]:
        """Cache and return (ip, port) for a given host ID."""
        if host_id not in self.host_iface_map:
            res = self._rpc(
                "host.get",
                {"hostids": [host_id], "output": ["hostid"], "selectInterfaces": ["type", "ip", "dns", "port"]}
            )
            iface = next(
                (i for i in res[0]["interfaces"] if int(i["type"]) == 1),
                res[0]["interfaces"][0]
            )
            ip = iface["ip"] or iface["dns"]
            port = int(iface["port"])
            self.host_iface_map[host_id] = (ip, port)
        return self.host_iface_map[host_id]


class PushHandler(BaseHTTPRequestHandler):
    """
    HTTP handler for incoming Zabbix push alerts.
    Expects POST /alert with Zabbix JSON; enriches via ZabbixPushHelper, converts
    via ZabbixConverter, then forwards to IDMEFv2Client.
    """
    converter:   ZabbixConverter
    client:      IDMEFv2Client
    helper:      ZabbixPushHelper
    server_info: dict[str, Any]

    def log_message(self, *_args, **_kwargs) -> None:
        # disable base class logging
        return

    def do_POST(self) -> None:
        if self.path != "/alert":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            src = json.loads(body)
        except Exception as exc:
            log.error("Invalid JSON in push: %s", exc)
            self.send_error(400, "Bad Request – invalid JSON")
            return

        log.debug("Received push JSON: %s", src)

        try:
            # 1) fetch problem clock
            eid = str(src.get("eventid", ""))
            if not eid:
                raise ValueError("Missing eventid field")
            prob = self.helper._rpc("problem.get", {"eventids": [eid], "output": ["clock"]})
            if not prob:
                raise RuntimeError(f"eventid {eid} not found")
            src["clock"] = prob[0]["clock"]

            # 2) fetch host/interface details
            tid = self.helper._rpc("problem.get", {"eventids": [eid], "output": ["objectid"]})[0]["objectid"]
            hid = self.helper._get_hostid_for_trigger(tid)
            ip, port = self.helper._get_iface_for_host(hid)
            host_name = self.helper.trigger_host_map.get(f"name_{tid}", "unknown")

            # 3) fetch trigger description & severity
            trg = self.helper._rpc(
                "trigger.get",
                {"triggerids": [tid], "output": ["description", "priority"]}
            )[0]
            src["name"] = trg.get("description", src.get("name", ""))
            src["severity"] = str(trg.get("priority", src.get("severity", "0")))

            # 4) fill any missing fields
            src.setdefault("hosts",     [{"name": host_name}])
            src.setdefault("extra",     {"ip": ip, "port": port})
            src["extra_target"] = self.helper.server_info

            ok, msg = self.converter.convert(src)
            if ok:
                self.client.post(msg)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as exc:
            log.exception("Push-handler error")
            self.send_error(500, f"Internal Server Error: {exc}")