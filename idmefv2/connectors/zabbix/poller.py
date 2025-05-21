"""
Poll the Zabbix JSON‑RPC API for new problems and forward them to IDMEFv2.

• Zabbix ≥ 7.2: Bearer‑token auth
• Injects both Source (host) and Target (server) info into each message.
"""
from __future__ import annotations
import logging
import socket
import time
from typing import Any
from urllib.parse import urlparse

import requests

from .zabbixconverter import ZabbixConverter
from ..idmefv2client import IDMEFv2Client

log = logging.getLogger("zabbix-poller")


class ZabbixPoller:
    """Continuously polls Zabbix and relays new problems as IDMEFv2 messages."""

    def __init__(
        self,
        *,
        url: str,
        user: str,
        password: str,
        client: IDMEFv2Client,
        poll_interval: int = 30,
    ) -> None:
        # strip trailing slash for consistency
        self.url = url.rstrip("/")
        self.user = user
        self.password = password
        self.client = client
        self.poll_interval = poll_interval

        # parse server info for Target
        parsed = urlparse(self.url)
        host = parsed.hostname or "unknown"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            ip = host  # fallback to hostname if resolution fails
        self.server_info = {"hostname": host, "ip": ip, "port": port}

        self.session = requests.Session()
        self.token: str | None = None
        self.seen_eventids: set[str] = set()
        self.trigger_host_map: dict[str, str] = {}
        self.host_iface_map: dict[str, tuple[str, int]] = {}

        self.converter = ZabbixConverter()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _rpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        r = self.session.post(self.url, json=payload, headers=self._headers(), timeout=5)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        return data["result"]

    def login(self) -> None:
        """Authenticate and set Bearer token."""
        resp = self.session.post(
            self.url,
            json={"jsonrpc": "2.0", "id": 1, "method": "user.login",
                  "params": {"username": self.user, "password": self.password}},
            timeout=5,
        ).json()
        if "error" in resp:
            raise RuntimeError(resp["error"])
        self.token = resp["result"]
        log.info("Authenticated to Zabbix API (token %s…)", self.token[:8])

    def _get_hostid_for_trigger(self, trigger_id: str) -> str:
        if trigger_id not in self.trigger_host_map:
            res = self._rpc(
                "trigger.get",
                {
                    "triggerids": [trigger_id],
                    "output": ["triggerid"],
                    "selectHosts": ["hostid", "name"]
                },
            )
            host = res[0]["hosts"][0]
            self.trigger_host_map[trigger_id] = host["hostid"]
            self.trigger_host_map[f"name_{trigger_id}"] = host["name"]
        return self.trigger_host_map[trigger_id]

    def _get_iface_for_host(self, host_id: str) -> tuple[str, int]:
        if host_id not in self.host_iface_map:
            res = self._rpc(
                "host.get",
                {
                    "hostids": [host_id],
                    "output": ["hostid"],
                    "selectInterfaces": ["type", "ip", "dns", "port"]
                },
            )
            iface = next(
                (i for i in res[0]["interfaces"] if int(i["type"]) == 1),
                res[0]["interfaces"][0]
            )
            ip = iface["ip"] or iface["dns"]
            port = int(iface["port"])
            self.host_iface_map[host_id] = (ip, port)
        return self.host_iface_map[host_id]

    def run(self) -> None:
        # 1) authenticate once
        if not self.token:
            self.login()

        # 2) seed seen_eventids to skip existing problems
        initial = self._rpc(
            "problem.get",
            {"output": ["eventid"], "sortfield": "eventid", "sortorder": "ASC", "recent": True},
        )
        for p in initial:
            self.seen_eventids.add(p["eventid"])
        log.info("Seeded seen_eventids with %d active problems", len(self.seen_eventids))

        # 3) main loop: only new events
        while True:
            try:
                problems = self._rpc(
                    "problem.get",
                    {
                        "output": "extend",
                        "sortfield": "eventid",
                        "sortorder": "ASC",
                        "recent": True
                    },
                )
                for prob in problems:
                    eid = prob["eventid"]
                    if eid in self.seen_eventids:
                        continue
                    self.seen_eventids.add(eid)

                    tid = prob["objectid"]
                    hid = self._get_hostid_for_trigger(tid)
                    ip, port = self._get_iface_for_host(hid)
                    host_name = self.trigger_host_map.get(f"name_{tid}", "unknown")

                    prob["hosts"] = [{"name": host_name}]
                    prob["extra"] = {"ip": ip, "port": port}
                    prob["extra_target"] = self.server_info

                    forward, idmef = self.converter.convert(prob)
                    if forward:
                        self.client.post(idmef)

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                log.info("Interrupted by user")
                break
            except Exception as exc:
                log.exception("Polling error: %s", exc)
                time.sleep(self.poll_interval)
