
import argparse
import logging
import sys
from configparser import ConfigParser
import yaml
from idmefv2.connectors.suricata.eveserver import EVESocketServer, EVEFileServer

class Configuration(ConfigParser):
    def __init__(self, filename):
        super().__init__()

        self.read(filename)

def parse_options():
    parser = argparse.ArgumentParser(description='Launch the EVE to IDMEFv2 conversion server')
    parser.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')
    return parser.parse_args()


def find_eve_output(filename):
    with open(filename) as f:
        cfg = yaml.safe_load(f)
        r = [x for x in cfg['outputs'] if 'eve-log' in x]
        el= r[0]['eve-log']
        if el['enabled']:
            return (el['filetype'], el['filename'])
    logging.error('error loading Suricata config file')
    sys.exit(1)

def main():
    options = parse_options()
    config = Configuration(options.conf_file)

    level = config.get('logging', 'level', fallback='INFO')
    logging.basicConfig(level=level)

    idmefv2_url = config.get('idmefv2', 'url')

    suricata_config = config.get('suricata', 'config')
    filetype, filename = find_eve_output(suricata_config)

    if filetype not in ['unix_stream', 'regular']:
        logging.error("configuration option suricata.eve must be one of ['unix_stream', 'regular']")
        sys.exit(1)

    server = None
    if filetype == 'unix_stream':
        server = EVESocketServer(url = idmefv2_url, path = filename)
    elif filetype == 'regular':
        server = EVEFileServer(url = idmefv2_url, path = filename)

    server.run()

if __name__ == '__main__':
    main()
