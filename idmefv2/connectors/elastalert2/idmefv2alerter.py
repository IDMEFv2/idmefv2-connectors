'''
Module containing IDMEFv2 alerter
'''
from elastalert.alerts import Alerter
from ..idmefv2client import IDMEFv2Client

class IDMEFv2Alerter(Alerter):
    '''
    Class for generating IDMEFv2 alerts from elastalert2
    '''
    required_options = set(['idmefv2_url'])

    def __init__(self, rule):
        super().__init__(rule)
        url = self.rule['idmefv2_url']
        login = self.rule.get('idmefv2_login')
        password = self.rule.get('idmefv2_password')
        verify = self.rule.get('idmefv2_verify', True)
        self._idmefv2_client = IDMEFv2Client(url, login=login, password=password, verify=verify)

    def alert(self, match):
        self._idmefv2_client.post(match)

    def get_info(self):
        return {'type': 'IDMEFv2 Alerter',
                'url': self.rule['idmefv2_url']}
