'''
Main for Suricata connector
'''
import argparse
import logging
import os.path
import sys
from configparser import ConfigParser
import yaml
from .eveserver import EVESocketServer, EVEFileServer
from ..idmefv2client import IDMEFv2Client

class Configuration(ConfigParser):
    '''
    Configuration using ConfigParser
    '''
    def __init__(self, filename):
        super().__init__()

        self.read(filename)

def parse_options():
    '''
    Parse command line options

    Returns:
        Namespace: parsed command line options
    '''
    parser = argparse.ArgumentParser(description='Launch the EVE to IDMEFv2 conversion server')
    parser.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')
    return parser.parse_args()


def find_eve_output(filename: str):
    '''
    Reads Suricata YAML configuration file in order to find EVE output configuration fields

    Args:
        filename (str): path to the Suricata configuration file

    Raises:
        KeyError: if needed keys not found in configuration fields
        ValueError: if EVE output disabled

    Returns:
        (filetype, filename) tuple if found and enabled
    '''
    with open(filename, 'rb') as f:
        suricata_config = yaml.safe_load(f)
        # suricata_config['outputs'] is a list of dict
        outputs = (output for output in suricata_config['outputs'] if 'eve-log' in output)
        eve_log_output = next(outputs, None)
        if eve_log_output is None:
            raise KeyError('eve-log not found in outputs')
        eve_log = eve_log_output['eve-log']
        enabled = eve_log.get('enabled', False)
        filetype = eve_log.get('filetype')
        filename = eve_log.get('filename')
        if not enabled:
            raise ValueError('EVE output is disabled')
        if filetype is None or filename is None:
            raise KeyError('filetype or filename not found')
        if not os.path.isabs(filename):
            default_log_dir = suricata_config.get('default-log-dir')
            if default_log_dir is None:
                raise KeyError('filename is relative and no default-log-dir defined')
            filename = os.path.join(default_log_dir, filename)
        return (filetype, filename)

def main():
    '''
    Main function:
        - read configuration file
        - set logging level
        - creates the IDMEFv2 HTTP client
        - parse Suricata configuration file
        - according to EVE output configuration, launch the EVE server
    '''
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
    filetype, filename = find_eve_output(suricata_config)
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
