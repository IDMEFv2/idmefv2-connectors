"""
Main module of the Prometheus-IDMEFv2 Connector.

Contains the program's entrypoint with polling mode of operation.
Polls the Prometheus /api/v1/alerts endpoint for active alerts.
"""

from __future__ import annotations

import logging

from .poller import PrometheusPoller
from .prometheusconverter import PrometheusConverter
from ..connector import ConnectorArgumentParser, Configuration, Connector


log = logging.getLogger("prometheus-connector")


class PollingConnector(Connector):
    """Periodically polls alerts from Prometheus and sends them as IDMEFv2."""

    def __init__(self, cfg: Configuration, converter: PrometheusConverter):
        """
        Initialize the polling connector.

        Args:
            cfg: Configuration object with connector settings.
            converter: PrometheusConverter instance for alert transformation.
        """
        super().__init__("prometheus", cfg, converter)

        prometheus_url = cfg.get("prometheus", "url")
        poll_interval = int(cfg.get("prometheus", "poll_interval", fallback="30"))
        disable_seeding = cfg.getboolean(
            "prometheus", "disable_seeding", fallback=False
        )

        self.poller = PrometheusPoller(
            prometheus_url=prometheus_url,
            client=self.idmefv2_client,
            converter=converter,
            poll_interval=poll_interval,
            disable_seeding=disable_seeding,
        )

    def run(self):
        """Start the polling loop."""
        self.logger.info("Starting polling connector")
        self.poller.run()


def main():
    """Parse arguments, load configuration, and start the connector."""
    opts = ConnectorArgumentParser("prometheus").parse_args()
    cfg = Configuration(opts)
    converter = PrometheusConverter()
    connector = PollingConnector(cfg, converter)
    connector.run()


if __name__ == "__main__":
    main()
