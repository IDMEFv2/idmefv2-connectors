'''
Main for Wazuh connector
'''
import json
import logging
import sys
from .wazuhconverter import WazuhConverter
from ..filetailer import FileTailer
from ..connector import Connector

class WazuhConnector(Connector):
    '''
    Class for Wazuh connector
    '''
    def __init__(self):
        super().__init__('wazuh')
        self.log_path = self.config.get('wazuh', 'logfile')
        self.converter = WazuhConverter()

    def run(self):
        '''
        Run the connector: loop
            - receiving JSON alert
            - converting alert to IDMEFv2
            - sending converted alert to IDMEFv2 server
        '''
        log = logging.getLogger('wazuh-connector')

        log.info("Tailing from file %s", self.log_path)

        ft = FileTailer(self.log_path)
        try:
            ft.wait_for_file()
        except FileNotFoundError:
            log.critical("cannot read file %s", self.log_path)
            sys.exit(1)

        for line in ft.tail():
            log.debug("received %s", line)
            wazuh_alert = json.loads(line)
            (converted, idmefv2_alert) = self.converter.convert(wazuh_alert)
            if converted:
                self.idmefv2_client.post(idmefv2_alert)

if __name__ == '__main__':
    WazuhConnector().run()
