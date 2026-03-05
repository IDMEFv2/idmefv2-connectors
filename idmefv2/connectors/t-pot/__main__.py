"""
The T-Pot connector main.

Polls Elasticsearch for T-Pot honeypot events
and converts them to IDMEFv2 format.
"""
from __future__ import annotations

import logging

from .poller import TpotPoller
from .tpotconverter import TpotConverter
from ..connector import ConnectorArgumentParser, Configuration, Connector

log = logging.getLogger("tpot-connector")


class TpotConnector(Connector):
    """The T-Pot polling connector."""

    def __init__(self, cfg: Configuration):
        """
        Initialize the T-Pot connector.

        Args:
            cfg: Configuration object with connector settings.
        """
        converter = TpotConverter()
        super().__init__("tpot", cfg, converter)

        elasticsearch_url = cfg.get("tpot", "elasticsearch_url")
        poll_interval = int(
            cfg.get("tpot", "poll_interval", fallback="30")
        )
        index_pattern = cfg.get(
            "tpot", "index_pattern", fallback="logstash-*"
        )

        catch_up = cfg.getboolean("tpot", "catch_up", fallback=False)

        self.poller = TpotPoller(
            elasticsearch_url=elasticsearch_url,
            index_pattern=index_pattern,
            client=self.idmefv2_client,
            converter=converter,
            poll_interval=poll_interval,
            catch_up=catch_up
        )

    def run(self):
        """Start the polling loop."""
        self.logger.info("Starting T-Pot polling connector")
        self.poller.run()


def main():
    """Parse arguments, load configuration, and start the connector."""
    opts = ConnectorArgumentParser("tpot").parse_args()
    cfg = Configuration(opts)
    connector = TpotConnector(cfg)
    connector.run()


if __name__ == "__main__":
    main()
