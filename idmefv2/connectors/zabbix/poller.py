"""
Poll the Zabbix JSON‑RPC API for new problems and forward them to IDMEFv2.

• Zabbix ≥ 7.2: Bearer‑token auth
• Injects both Source (host) and Target (server) info into each message.
"""
from __future__ import annotations
import logging
import time
from typing import Any

import requests

from .zabbixconverter import ZabbixConverter, ZabbixCloseConverter
from ..idmefv2client import IDMEFv2Client
from .models import ZabbixAuth, ZabbixCache, _ZabbixContext
from .zabbixutil import (
    perform_rpc,
    get_hostid_for_trigger,
    get_iface_for_host,
    resolve_zabbix_server_info,
    load_alert_state,
    save_alert_state,
)

log = logging.getLogger("zabbix-poller")


# pylint: disable=too-many-instance-attributes
class ZabbixPoller:
    """Continuously polls Zabbix and relays new problems as IDMEFv2 messages."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        auth: ZabbixAuth,
        client: IDMEFv2Client,
        poll_interval: int = 30,
    ) -> None:
        self.client = client
        self.poll_interval = poll_interval
        self.cache = ZabbixCache()
        self.converter = ZabbixConverter()
        self.close_converter = ZabbixCloseConverter()
        self.alert_state = load_alert_state()

        server_info = resolve_zabbix_server_info(auth.url)
        server_info.poll_interval = poll_interval

        self.ctx = _ZabbixContext(
            auth=auth,
            session=requests.Session(),
            token=None,
            server_info=server_info,
        )

    def login(self) -> None:
        """Authenticate and set Bearer token."""
        resp = self.ctx.session.post(
            self.ctx.auth.url.rstrip("/"),
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "user.login",
                "params": {
                    "username": self.ctx.auth.user,
                    "password": self.ctx.auth.password,
                },
            },
            timeout=5,
        ).json()
        if "error" in resp:
            raise RuntimeError(resp["error"])
        self.ctx.token = resp["result"]
        log.info("Authenticated to Zabbix API (token %s…)", self.ctx.token[:8])

    def _rpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        return perform_rpc(
            self.ctx.session,
            self.ctx.auth.url.rstrip("/"),
            self.ctx.token,
            method,
            params,
        )

    def _send_close_alert(self, prob: dict[str, Any], tid: str, eid: str, r_eventid: str) -> None:
        """
        Send an IDMEFv2 "Closed" update for a resolved problem, chained via
        PredID to the last alert sent for this trigger. Source/Target are
        inherited from that previous alert, since the resolved problem
        itself carries no host/interface info.
        """
        previous = self.alert_state.get(tid, {})
        close_src = {
            "name": prob["name"],
            "severity": prob["severity"],
            "clock": prob.get("r_clock") or prob["clock"],
            "pred_id": previous.get("ID"),
            "source": previous.get("Source", []),
            "target": previous.get("Target", []),
        }
        forward, idmef = self.close_converter.convert(close_src)
        if forward:
            self.client.post(idmef)
            self.alert_state[tid] = idmef
            save_alert_state(self.alert_state)
            log.info(
                "Inviato alert di chiusura per eventid=%s (r_eventid=%s, r_clock=%s)",
                eid, r_eventid, prob.get("r_clock"),
            )

    def run(self) -> None:
        """
        Starts polling from Zabbix.
        """
        if not self.ctx.token:
            self.login()

        # Seed seen_eventids to skip existing problems
        initial = self._rpc(
            "problem.get",
            {
                "output": ["eventid"],
                "sortfield": "eventid",
                "sortorder": "ASC",
                "recent": True,
            },
        )
        for p in initial:
            self.cache.seen_eventids.add(p["eventid"])
        log.info(
            "Seeded seen_eventids with %d active problems", len(self.cache.seen_eventids)
        )

        # Main loop: only process new problems
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
                    tid = prob["objectid"]

                    if eid in self.cache.seen_eventids:
                        r_eventid = prob.get("r_eventid", "0")
                        if r_eventid != "0" and eid not in self.cache.closed_eventids:
                            self.cache.closed_eventids.add(eid)
                            self._send_close_alert(prob, tid, eid, r_eventid)
                        continue
                    self.cache.seen_eventids.add(eid)

                    hid = get_hostid_for_trigger(
                        self.ctx.session,
                        self.ctx.auth.url,
                        self.ctx.token,
                        tid,
                        self.cache,
                    )
                    ip, port = get_iface_for_host(
                        self.ctx.session,
                        self.ctx.auth.url,
                        self.ctx.token,
                        hid,
                        self.cache,
                    )
                    host_name = self.cache.trigger_host_map.get(f"name_{tid}", "unknown")

                    prob["hosts"] = [{"name": host_name}]
                    prob["extra"] = {"ip": ip, "port": port}
                    prob["extra_target"] = {
                        "hostname": self.ctx.server_info.hostname,
                        "ip": self.ctx.server_info.ip,
                        "port": self.ctx.server_info.port,
                    }
                    prob["pred_id"] = self.alert_state.get(tid, {}).get("ID")

                    forward, idmef = self.converter.convert(prob)
                    if forward:
                        self.client.post(idmef)
                        self.alert_state[tid] = idmef
                        save_alert_state(self.alert_state)

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                log.info("Interrupted by user")
                break
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.exception("Polling error: %s", exc)
                time.sleep(self.poll_interval)
