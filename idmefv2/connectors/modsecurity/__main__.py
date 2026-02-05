"""
Main module of the ModSecurity-IDMEFv2 Connector.

Reads ModSecurity JSON audit logs and converts them to IDMEFv2 format.
"""

from __future__ import annotations

from .modsecurityconverter import ModSecurityConverter
from ..connector import ConnectorArgumentParser, Configuration, LogFileConnector


def main():
    """Parse arguments, load configuration, and start the connector."""
    opts = ConnectorArgumentParser("modsecurity").parse_args()
    cfg = Configuration(opts)
    log_file = cfg.get("connector", "log_file")
    converter = ModSecurityConverter()
    connector = LogFileConnector("modsecurity", cfg, converter, log_file)
    connector.run()


if __name__ == "__main__":
    main()
