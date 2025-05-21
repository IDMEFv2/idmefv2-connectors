from __future__ import annotations
import logging
import socket
from http.server import HTTPServer
from urllib.parse import urlparse

from .push import ZabbixPushHelper, PushHandler
from .poller import ZabbixPoller
from .zabbixconverter import ZabbixConverter
from ..connector import Configuration, Runner

log = logging.getLogger("zabbix-connector")

class PollingRunner(Runner):
    def __init__(self, cfg: Configuration, converter: ZabbixConverter):
        super().__init__(cfg, converter)

        self.poller = ZabbixPoller(
            url=cfg.get("zabbix", "url"),
            user=cfg.get("zabbix", "user"),
            password=cfg.get("zabbix", "password"),
            client=self.idmefv2_client,
            poll_interval=cfg.getint("zabbix", "poll_interval", fallback=30)
        )
        self.poller.converter = converter

    def run(self):
        self.logger.info("Starting polling runner")
        self.poller.run()


class PushRunner(Runner):
    def __init__(self, cfg: Configuration, converter: ZabbixConverter):
        super().__init__(cfg, converter)

        zbx_url = cfg.get("zabbix", "url")
        zbx_user = cfg.get("zabbix", "user")
        zbx_pass = cfg.get("zabbix", "password")

        self.helper = ZabbixPushHelper(url=zbx_url, user=zbx_user, password=zbx_pass)
        self.helper.login()

        # Server info setup
        parsed = urlparse(zbx_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            ip = host

        server_info = {"hostname": host, "ip": ip, "port": port}

        # Set static attributes on PushHandler
        PushHandler.converter = converter
        PushHandler.client = self.idmefv2_client
        PushHandler.helper = self.helper
        PushHandler.server_info = server_info

        listen = cfg.get("connector", "listen_address", fallback="0.0.0.0")
        lport = cfg.getint("connector", "listen_port", fallback=9090)
        self.server = HTTPServer((listen, lport), PushHandler)
        self.listen_address = listen
        self.listen_port = lport

    def run(self):
        self.logger.info("HTTP server listening on %s:%d/alert",
                         self.listen_address,
                         self.listen_port)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.server.server_close()


def main():
    cfg = Configuration("zabbix")
    mode = cfg.get("connector", "mode", fallback="polling").lower()
    if mode not in ("polling", "push"):
        raise ValueError("Mode must be either 'polling' or 'push'")

    converter = ZabbixConverter([mode])
    if mode == "polling":
        runner = PollingRunner(cfg, converter)
    else:
        runner = PushRunner(cfg, converter)
    runner.run()


if __name__ == "__main__":
    main()
