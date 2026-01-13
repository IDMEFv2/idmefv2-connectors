"""
Main module of the Zabbix-IDMEFv2 Connector.

Contains the program's entripoint, with two modes of operation:
- polling: Automatic scheduled execution
- push: Starts an HTTP server to receive the alerts from Zabbix
"""

from __future__ import annotations
import logging
from http.server import HTTPServer

from .push import ZabbixPushHelper, PushHandler
from .poller import ZabbixPoller
from .zabbixconverter import ZabbixConverter
from ..connector import ConnectorArgumentParser, Configuration, Connector
from .models import ZabbixAuth


log = logging.getLogger("zabbix-connector")

class PollingConnector(Connector):
    """Periodically executes a polling of the events from Zabbix and sends them."""
    def __init__(self, cfg: Configuration, converter: ZabbixConverter):
        super().__init__("zabbix", cfg, converter)

        auth = ZabbixAuth(
            url=cfg.get("zabbix", "url"),
            user=cfg.get("zabbix", "user"),
            password=cfg.get("zabbix", "password")
        )

        self.poller = ZabbixPoller(
            auth = auth,
            client=self.idmefv2_client,
            poll_interval=int(cfg.get("zabbix", "poll_interval", fallback=30))
        )
        self.poller.converter = converter

    def run(self):
        self.logger.info("Starting polling runner")
        self.poller.run()

class PushConnector(Connector):
    """Starts an HTTP server to receive events from Zabbix and send them."""
    def __init__(self, cfg: Configuration, converter: ZabbixConverter):
        super().__init__("zabbix", cfg, converter)

        zbx_url = cfg.get("zabbix", "url")
        zbx_user = cfg.get("zabbix", "user")
        zbx_pass = cfg.get("zabbix", "password")

        auth = ZabbixAuth(url=zbx_url, user=zbx_user, password=zbx_pass)
        self.helper = ZabbixPushHelper(auth=auth)
        self.helper.login()

        # Use server_info from helper (dataclass) and convert to dict
        server_info = self.helper.server_info.__dict__

        # Set static attributes on PushHandler
        PushHandler.converter = converter
        PushHandler.client = self.idmefv2_client
        PushHandler.helper = self.helper
        PushHandler.server_info = server_info

        listen = cfg.get("connector", "listen_address", fallback="0.0.0.0")
        lport_str = cfg.get("connector", "listen_port", fallback=9090)
        lport = int(lport_str)
        self.server = HTTPServer((listen, lport), PushHandler)
        self.listen_address = listen
        self.listen_port = lport

    def run(self):
        self.logger.info(
            "HTTP server listening on %s:%d/alert",
            self.listen_address,
            self.listen_port
            )
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.server.server_close()

def main():
    """Chooses the correct execution mode based on the configuration the user provides."""
    opts = ConnectorArgumentParser("zabbix").parse_args()
    cfg = Configuration(opts)
    mode = cfg.get("connector", "mode", fallback="polling").lower()
    if mode not in ("polling", "push"):
        raise ValueError("Mode must be either 'polling' or 'push'")

    converter = ZabbixConverter([mode])
    if mode == "polling":
        connector = PollingConnector(cfg, converter)
    else:
        connector = PushConnector(cfg, converter)
    connector.run()

if __name__ == "__main__":
    main()
