'''
Base connector
'''
import abc
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
import json
import logging
import sys
from typing import Union
import requests
from .idmefv2client import IDMEFv2Client
from .jsonconverter import JSONConverter
from .filetailer import FileTailer

class ConnectorArgumentParser(ArgumentParser):
    '''
    Base class for connector command line argument parsing:
        - add -c/--conf option to give configuration file
    '''
    def __init__(self, name: str):
        description = f"Launch the {name.capitalize()} to IDMEFv2 connector"
        super().__init__(description=description)
        self.add_argument('-c', '--conf', help='give configuration file', dest='conf_file')

class Configuration(ConfigParser):
    '''
    Base class for connectors configuration:
        - read configuration file
    '''

    def __init__(self, opts: Namespace):
        '''
        Constructor:
            - read configuration file
        '''
        super().__init__()
        self.read(opts.conf_file)

class Connector(abc.ABC):
    '''
    Base class for connectors
    '''

    def __init__(self, name: str, cfg: Configuration, converter: JSONConverter):
        '''
        Main function:
            - set logging level
            - creates the IDMEFv2 HTTP client
        '''
        level = cfg.get('logging', 'level', fallback='INFO')
        logging.basicConfig(level=level)
        self.logger = logging.getLogger(name + '-connector')

        url = cfg.get('idmefv2', 'url')
        login = cfg.get('idmefv2', 'login', fallback=None)
        password = cfg.get('idmefv2', 'password', fallback=None)
        self.idmefv2_client = IDMEFv2Client(url=url, login=login, password=password)

        self.converter = converter

    def alert(self, b: Union[str,bytes]):
        '''
        Process an alert:
            - converts parameter to JSON
            - call converter
            - if alert was converted, send it to IDMEFv2 server

        Args:
            b (Union[str,bytes]): the origin alert
        '''
        self.logger.debug("received %s", b)
        alert = json.loads(b)
        (converted, idmefv2_alert) = self.converter.convert(alert)
        if converted:
            self.logger.info("sending IDMEFv2 alert %s", str(idmefv2_alert))
            try:
                self.idmefv2_client.post(idmefv2_alert)
            except requests.RequestException as e:
                self.logger.error('POST failed with error %s', str(e))

    @abc.abstractmethod
    def run(self):
        '''
        Connector loop, implemented in sub-classes

        Raises:
            NotImplementedError: must be implemented in concrete sub-classes
        '''
        raise NotImplementedError

class LogFileConnector(Connector):
    '''
    Runner for log file
    '''
    def __init__(self, name: str, cfg: Configuration, converter: JSONConverter, log_file_path: str):
        '''
        Main function:
            - read configuration file
            - set logging level
            - creates the IDMEFv2 HTTP client
        '''
        super().__init__(name, cfg, converter)
        self.log_file_path = log_file_path

    def run(self):
        '''
        Run the connector on a log file: loop
            - receiving JSON alert by 'tailing' the log file
            - converting alert to IDMEFv2
            - sending converted alert to IDMEFv2 server
        '''
        self.logger.info("Tailing from file %s", self.log_file_path)

        ft = FileTailer(self.log_file_path)
        try:
            ft.wait_for_file()
        except FileNotFoundError:
            self.logger.critical("cannot read file %s", self.log_file_path)
            sys.exit(1)

        for line in ft.tail():
            self.alert(line)
