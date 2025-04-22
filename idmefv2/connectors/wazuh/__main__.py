'''
Main for Wazuh connector
'''
import argparse
from configparser import ConfigParser
import json
import logging
import sys
from .wazuhconverter import WazuhConverter
from ..idmefv2client import IDMEFv2Client
from ..filetailer import FileTailer

def parse_options():
    '''
    Parse command line options

    Returns:
        Namespace: parsed command line options
    '''
    parser = argparse.ArgumentParser(description='Launch the Wazuh to IDMEFv2 connector')
    parser.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')
    return parser.parse_args()

def _run(wazuh_log_path: str, idmefv2_client: IDMEFv2Client):
    log = logging.getLogger('wazuh-connector')

    ft = FileTailer(wazuh_log_path)
    try:
        ft.wait_for_file()
    except FileNotFoundError:
        log.error("cannot read file %s", wazuh_log_path)
        sys.exit(1)

    converter = WazuhConverter()

    for line in ft.tail():
        log.debug("received %s", str(line))
        wazuh_alert = json.loads(line)
        (converted, idmefv2_alert) = converter.convert(wazuh_alert)

        if converted:
            idmefv2_client.post(idmefv2_alert)

def main():
    '''
    Main function:
        - read configuration file
        - set logging level
        - creates the IDMEFv2 HTTP client
        - launch the log file poller
    '''
    options = parse_options()
    config = ConfigParser()
    config.read(options.conf_file)

    level = config.get('logging', 'level', fallback='INFO')
    logging.basicConfig(level=level)
    log = logging.getLogger('wazuh-connector')

    idmefv2_url = config.get('idmefv2', 'url')
    idmefv2_login = config.get('idmefv2', 'login', fallback=None)
    idmefv2_password = config.get('idmefv2', 'password', fallback=None)
    idmefv2_client = IDMEFv2Client(url=idmefv2_url, login=idmefv2_login, password=idmefv2_password)

    wazuh_log_path = config.get('wazuh', 'logfile')
    log.info("Tailing from file %s", wazuh_log_path)

    _run(wazuh_log_path, idmefv2_client)

if __name__ == '__main__':
    main()
