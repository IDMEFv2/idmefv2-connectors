
import argparse
import logging
import sys
from configparser import ConfigParser
from idmefv2.connectors.suricata.eveserver import EVESocketServer, EVEFileServer

class Configuration(ConfigParser):
    def __init__(self, filename):
        super().__init__()

        self.read(filename)

def parse_options():
    parser = argparse.ArgumentParser(description='Launch the EVE to IDMEFv2 conversion server')
    parser.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')
    return parser.parse_args()

def main():
    options = parse_options()
    config = Configuration(options.conf_file)

    level = config.get('logging', 'level', fallback='INFO')
    logging.basicConfig(level=level)

    idmefv2_url = config.get('idmefv2', 'url')

    server = None
    eve_output = config.get('suricata', 'eve')
    if eve_output == 'unix_stream':
        socket_path = config.get('suricata', 'unixsocket')
        server = EVESocketServer(url = idmefv2_url, path = socket_path)
    elif eve_output == 'regular':
        filename = config.get('suricata', filename)
        server = EVEFileServer(url = idmefv2_url, path = filename)

    if server is None:
        print('configuration option suricata.eve must be one of [unix_stream, regular]', file=sys.stderr)
        sys.exit(1)

    server.run()

if __name__ == '__main__':
    main()
