
import argparse
import logging
import sys
from configparser import ConfigParser
import yaml
from .eveserver import EVESocketServer, EVEFileServer
from ..idmefv2client import IDMEFv2Client

class Configuration(ConfigParser):
    def __init__(self, filename):
        super().__init__()

        self.read(filename)

def parse_options():
    parser = argparse.ArgumentParser(description='Launch the EVE to IDMEFv2 conversion server')
    parser.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')
    return parser.parse_args()


def find_eve_output(filename):
    with open(filename, 'rb') as f:
        cfg = yaml.safe_load(f)
        r = [x for x in cfg['outputs'] if 'eve-log' in x]
        el= r[0]['eve-log']
        if el['enabled']:
            return (el['filetype'], el['filename'])
    return None

def main():
    options = parse_options()
    config = Configuration(options.conf_file)

    level = config.get('logging', 'level', fallback='INFO')
    logging.basicConfig(level=level)
    log = logging.getLogger('suricata-connector')

    idmefv2_url = config.get('idmefv2', 'url')
    idmefv2_login = config.get('idmefv2', 'login', fallback=None)
    idmefv2_password = config.get('idmefv2', 'password', fallback=None)
    idmefv2_client = IDMEFv2Client(url=idmefv2_url, login=idmefv2_login, password=idmefv2_password)

    suricata_config = config.get('suricata', 'config')
    eve_output = find_eve_output(suricata_config)
    if eve_output is None:
        log.error('error loading Suricata config file')
        sys.exit(1)

    filetype, filename = eve_output

    accepted_filetypes = ['unix_stream', 'regular']
    if filetype not in accepted_filetypes:
        log.error("configuration option suricata.eve must be one of %s", accepted_filetypes)
        sys.exit(1)

    server = None
    if filetype == 'unix_stream':
        server = EVESocketServer(idmefv2_client, filename)
    elif filetype == 'regular':
        server = EVEFileServer(idmefv2_client, filename)

    server.run()

if __name__ == '__main__':
    main()
