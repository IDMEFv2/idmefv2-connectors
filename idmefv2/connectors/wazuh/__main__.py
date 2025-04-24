'''
Main for Wazuh connector
'''
import json
import logging
import sys
from .wazuhconverter import WazuhConverter
from ..filetailer import FileTailer
from ..baseconnector import BaseConnector

def _main():
    wazuh_connector = BaseConnector('wazuh')

    log = logging.getLogger('wazuh-connector')

    wazuh_log_path = wazuh_connector.config.get('wazuh', 'logfile')
    log.info("Tailing from file %s", wazuh_log_path)

    ft = FileTailer(wazuh_log_path)
    try:
        ft.wait_for_file()
    except FileNotFoundError:
        log.critical("cannot read file %s", wazuh_log_path)
        sys.exit(1)

    converter = WazuhConverter()

    for line in ft.tail():
        log.debug("received %s", line)
        wazuh_alert = json.loads(line)
        (converted, idmefv2_alert) = converter.convert(wazuh_alert)
        if converted:
            wazuh_connector.idmefv2_client.post(idmefv2_alert)

if __name__ == '__main__':
    _main()
