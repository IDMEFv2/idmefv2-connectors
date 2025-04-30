from __future__ import annotations
import argparse
import logging
from configparser import ConfigParser
from http.server import HTTPServer
import socket
from urllib.parse import urlparse

from .push import ZabbixPushHelper, PushHandler
from .poller import ZabbixPoller
from .zabbixconverter import ZabbixConverter
from ..idmefv2client import IDMEFv2Client

log = logging.getLogger("zabbix-connector")


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Zabbix → IDMEFv2 connector")
    ap.add_argument("-c", "--conf", dest="conf_file", required=True,
                    help="Path to connector configuration file")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = ConfigParser()
    cfg.read(args.conf_file)

    # Logging setup
    level = cfg.get("logging", "level", fallback="INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Mode must be either 'polling' or 'push'
    mode = cfg.get("connector", "mode", fallback="polling").lower()
    if mode not in ("polling", "push"):
        raise ValueError("Mode must be either 'polling' or 'push'")
    methods = [mode]

    # Zabbix parameters
    zbx_url  = cfg.get("zabbix", "url")
    zbx_user = cfg.get("zabbix", "user")
    zbx_pass = cfg.get("zabbix", "password")
    poll_int = cfg.getint("zabbix", "poll_interval", fallback=30)

    # IDMEFv2 client
    client = IDMEFv2Client(
        url      = cfg.get("idmefv2", "url"),
        login    = cfg.get("idmefv2", "login",    fallback=None),
        password = cfg.get("idmefv2", "password", fallback=None),
    )

    if mode == "polling":
        converter = ZabbixConverter(methods)
        poller = ZabbixPoller(
            url=zbx_url, user=zbx_user, password=zbx_pass,
            client=client, poll_interval=poll_int
        )
        poller.converter = converter
        poller.run()
        return

    # PUSH mode
    log.info("Running in PUSH mode: connecting to Zabbix API")
    helper = ZabbixPushHelper(url=zbx_url, user=zbx_user, password=zbx_pass)
    helper.login()

    converter = ZabbixConverter(methods)

    # Prepare server metadata
    parsed = urlparse(zbx_url)
    host   = parsed.hostname or "unknown"
    port   = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        ip = host
    server_info = {"hostname": host, "ip": ip, "port": port}

    PushHandler.converter   = converter
    PushHandler.client      = client
    PushHandler.helper      = helper
    PushHandler.server_info = server_info

    listen = cfg.get("connector", "listen_address", fallback="0.0.0.0")
    lport  = cfg.getint("connector", "listen_port",    fallback=9090)
    srv    = HTTPServer((listen, lport), PushHandler)

    log.info("Connector HTTP %s listening on %s:%d/alert", mode.upper(), listen, lport)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        log.info("Interrupted by user")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()