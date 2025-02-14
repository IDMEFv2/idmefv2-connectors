import logging
import requests

log = logging.getLogger('idmefv2-client')

class IDMEFv2Client:
    def __init__(self, *, url: str, login: str = None, password: str = None):
        self.url = url
        self.login = login
        self.password = password

    def post(self, idmefv2: dict):
        log.info("sending IDMEFv2 alert %s", str(idmefv2))
        kwargs = {'json' : idmefv2, 'timeout' : 1.0}
        if self.login is not None and self.password is not None:
            kwargs['auth'] = (self.login, self.password)
        r = requests.post(self.url, **kwargs)
        log.debug("got response %s", r)
