'''
A HTTP client POSTing IDMEFv2 messages and logging response
'''
import requests
from .configuration import Configuration

# pylint: disable=too-few-public-methods
class IDMEFv2Client:
    '''
    Class storing client configuration and sending IDMEFv2 messages
    '''
    def __init__(self, cfg: Configuration):
        self._url = cfg.get('idmefv2', 'url')
        self._session = requests.Session()
        login = cfg.get('idmefv2', 'login', fallback=None)
        password = cfg.get('idmefv2', 'password', fallback=None)
        if login is not None and password is not None:
            self._session.auth = (login, password)
        self._session.verify = cfg.getboolean('idmefv2', 'verify', fallback=True)

    def post(self, idmefv2: dict):
        '''
        Sends a IDMEFv2 message as a HTTP POST request to server configured in constructor

        Args:
            idmefv2 (dict): the IDMEFv2 message, supposed to be valid
        '''
        kwargs = {'json' : idmefv2, 'timeout' : 1.0}
        r = self._session.post(self._url, **kwargs)
        r.raise_for_status()
