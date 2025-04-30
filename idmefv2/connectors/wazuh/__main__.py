'''
Main for Wazuh connector
'''
from .wazuhconverter import WazuhConverter
from ..connector import Configuration, LogFileRunner

if __name__ == '__main__':
    cfg = Configuration('wazuh')
    log_file_path = cfg.get('wazuh', 'logfile')
    runner = LogFileRunner(cfg, WazuhConverter(), log_file_path)
    runner.run()
