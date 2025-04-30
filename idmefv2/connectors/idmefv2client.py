'''
A HTTP client POSTing IDMEFv2 messages and logging response
'''
import requests

# pylint: disable=too-few-public-methods
class IDMEFv2Client:
    '''
    Class storing client configuration and sending IDMEFv2 messages
    '''
    def __init__(self, *, url: str, login: str = None, password: str = None):
        self.url = url
        self.login = login
        self.password = password

    def post(self, idmefv2: dict):
        '''
        Sends a IDMEFv2 message as a HTTP POST request to server configured in constructor

        Args:
            idmefv2 (dict): the IDMEFv2 message, supposed to be valid
        '''
        kwargs = {'json' : idmefv2, 'timeout' : 1.0}
        if self.login is not None and self.password is not None:
            kwargs['auth'] = (self.login, self.password)
        r = requests.post(self.url, **kwargs)
        r.raise_for_status()
