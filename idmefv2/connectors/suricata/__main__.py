
import asyncio
import argparse
import logging
from idmefv2.connectors.suricata.server import EVEServer

def parse_options():
    parser = argparse.ArgumentParser(description='Launch the EVE to IDMEFv2 conversion server')
    parser.add_argument('-s', '--socket', help='give path to Unix socket used by Suricata to output alerts in EVE format', dest='socket_path')
    parser.add_argument('-u', '--url', help='URL of IDMEFv2 server receiving converted alerts', dest='idmefv2_url')
    parser.add_argument('-d', '--debug', help='set log level to DEBUG', dest='log_debug', action='store_true')
    return parser.parse_args()

def main():
    options = parse_options()
    level = logging.DEBUG if options.log_debug else logging.INFO
    logging.basicConfig(level=level)
    server = EVEServer(options.socket_path, options.idmefv2_url)
    asyncio.run(server.start())

if __name__ == '__main__':
    main()
