'''
A HTTP client POSTing IDMEFv2 messages and logging response
'''
from typing import Union
import requests

# pylint: disable=too-few-public-methods
class IDMEFv2Client:
    '''
    Class storing client configuration and sending IDMEFv2 messages
    '''
    def __init__(self, url: str, login : str = None, password : str = None, verify : bool = True):
        self._url = url
        self._session = requests.Session()
        if login is not None and password is not None:
            self._session.auth = (login, password)
        self._session.verify = verify

    def post(self, idmefv2: Union[str, bytes, dict]):
        '''
        Sends a IDMEFv2 message as a HTTP POST request to server configured in constructor

        Args:
            idmefv2 (dict): the IDMEFv2 message, supposed to be valid
        '''
        kwargs = {'timeout' : 1.0}
        if isinstance(idmefv2, dict):
            kwargs ['json'] = idmefv2
        else:
            kwargs ['data'] = idmefv2
            kwargs['headers'] = {'Content-Type':'application/json'}
        r = self._session.post(self._url, **kwargs)
        r.raise_for_status()
