
import argparse
import logging
from idmefv2.connectors.suricata.eveserver import EVEServer
from configparser import ConfigParser

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

    socket_path = config.get('suricata', 'unixsocket')
    idmefv2_url = config.get('idmefv2', 'url')
    server = EVEServer(socket_path, idmefv2_url)
    server.start()

if __name__ == '__main__':
    main()
