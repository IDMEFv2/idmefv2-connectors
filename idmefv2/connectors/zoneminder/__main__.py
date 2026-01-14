"""
Main for zoneminder connector
"""

from .zoneminderconverter import ZoneminderConverter
from ..configuration import Configuration
from ..connector import ConnectorArgumentParser, LogFileConnector

if __name__ == "__main__":
    opts = ConnectorArgumentParser('zoneminder').parse_args()
    cfg = Configuration(opts)
    log_file_path = cfg.get('zmjson', 'logfile')
    connector = LogFileConnector('zoneminder', cfg, ZoneminderConverter(), log_file_path)
    connector.run()
