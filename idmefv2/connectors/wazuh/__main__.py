'''
Main for Wazuh connector
'''
from .wazuhconverter import WazuhConverter
from ..connector import ConnectorArgumentParser, Configuration, LogFileConnector

if __name__ == '__main__':
    opts = ConnectorArgumentParser('wazuh').parse_args()
    cfg = Configuration(opts)
    log_file_path = cfg.get('wazuh', 'logfile')
    connector = LogFileConnector(cfg, WazuhConverter(), log_file_path)
    connector.run()
