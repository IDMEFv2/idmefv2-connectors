'''
Module containing IDMEFv2 alerter
'''
import logging
import urllib3
from jinja2 import Environment
from requests import HTTPError
from elastalert.alerts import Alerter
from elastalert.util import elastalert_logger
from ..idmefv2client import IDMEFv2Client

urllib3.disable_warnings()

class IDMEFv2Alerter(Alerter):
    '''
    Class for generating IDMEFv2 alerts from elastalert2
    '''
    required_options = set(['idmefv2_url', 'idmefv2_template'])

    def __init__(self, rule):
        super().__init__(rule)

        url = self.rule['idmefv2_url']
        login = self.rule.get('idmefv2_login')
        password = self.rule.get('idmefv2_password')
        verify = self.rule.get('idmefv2_verify', True)
        self._idmefv2_client = IDMEFv2Client(url, login=login, password=password, verify=verify)

        self._template = Environment().from_string(self.rule.get('idmefv2_template'))

        elastalert_logger.setLevel(logging.DEBUG)
        elastalert_logger.debug("rule: %s\n\n", str(self.rule))

    def alert(self, match):
        for m in match:
            elastalert_logger.debug("match: %s\n\n", str(m))
            context = {'match': m, 'rule': self.rule}
            idmefv2 = self._template.render(context)
            elastalert_logger.debug(idmefv2)
            try:
                self._idmefv2_client.post(idmefv2)
            except HTTPError as e:
                elastalert_logger.warning("error posting alert %s", str(e))

    def get_info(self):
        return {'type': 'IDMEFv2 Alerter',
                'url': self.rule['idmefv2_url']}
