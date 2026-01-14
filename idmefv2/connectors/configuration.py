'''
Connector configuration
'''
from argparse import Namespace
from configparser import ConfigParser

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
