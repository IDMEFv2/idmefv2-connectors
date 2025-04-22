'''
Base connector
'''
import argparse
from configparser import ConfigParser
import logging
from .idmefv2client import IDMEFv2Client

# pylint: disable=too-few-public-methods
class BaseConnector:
    '''
    Base class for connectors:
        - parse command line
        - read configuration file
        - set logging level
        - creates the IDMEFv2 HTTP client
    '''

    def parse_options(self, name: str):
        '''
        Parse command line options

        Returns:
            Namespace: parsed command line options
        '''
        description = f"Launch the {name.capitalize()} to IDMEFv2 connector"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')
        return parser.parse_args()

    def __init__(self, name: str):
        '''
        Main function:
            - read configuration file
            - set logging level
            - creates the IDMEFv2 HTTP client
            - launch the log file poller
        '''
        options = self.parse_options(name)
        self.config = ConfigParser()
        self.config.read(options.conf_file)

        level = self.config.get('logging', 'level', fallback='INFO')
        logging.basicConfig(level=level)

        url = self.config.get('idmefv2', 'url')
        login = self.config.get('idmefv2', 'login', fallback=None)
        password = self.config.get('idmefv2', 'password', fallback=None)
        self.idmefv2_client = IDMEFv2Client(url=url, login=login, password=password)
