"""
Main for motion connector
"""

from .motionconverter import MotionConverter
from ..configuration import Configuration
from ..connector import ConnectorArgumentParser, LogFileConnector

if __name__ == "__main__":
    opts = ConnectorArgumentParser('motion').parse_args()
    cfg = Configuration(opts)
    log_file_path = cfg.get('motionjson', 'logfile')
    connector = LogFileConnector('motion', cfg, MotionConverter(), log_file_path)
    connector.run()
