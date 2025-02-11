'''
    The Unix socket server listening for EVE alerts
'''
import abc
import json
import logging
import os
import socketserver
import time
from typing import Union
import requests
import inotify.adapters
from idmefv2.connectors.suricata.suricataconverter import SuricataConverter

log = logging.getLogger('suricata-connector')

class EVEServer(abc.ABC):
    '''
        Base class for servers receiving EVE alerts
        On receiving an alert, convert it to IDMEFv2 and send it to a IDMEFv2 HTTPS server
    '''
    def __init__(self, *, url: str):
        self.idmefv2_url = url
        self.converter = SuricataConverter()

    def alert(self, b: Union[str,bytes]):
        eve_alert = json.loads(b)
        (converted, idmefv2_alert) = self.converter.convert(eve_alert)

        if converted:
            log.info("sending IDMEFv2 alert %s", str(idmefv2_alert))
            r = requests.post(self.idmefv2_url, json=idmefv2_alert, timeout=1.0)
            log.debug("got response %s", r)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

class EVEStreamRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        log.debug("received data %s", str(data))
        self.server.eve_server.alert(data)

class EVEUnixStreamServer(socketserver.UnixStreamServer):
    def __init__(self, eve_socket_server):
        super().__init__(eve_socket_server.socket_path, EVEStreamRequestHandler)
        self.eve_server = eve_socket_server

class EVESocketServer(EVEServer):
    '''
        A class implementing a server listening on a Unix socket for EVE alerts.
    '''
    def __init__(self, *, url: str, path: str):
        '''
            Parameters:
                path(str): path to the Unix socket
                url(str): the url of the IDMEFv2 HTTPS server
        '''
        super().__init__(url=url)
        self.socket_path = path

    def run(self):
        '''
            Start the server listening on Unix socket specified in constructor.
        '''
        with EVEUnixStreamServer(self) as server:
            log.info("Listening on Unix socket %s", self.socket_path)
            server.serve_forever()

        logging.info('Server closed')

class EVEFileServer(EVEServer):
    '''
        A class implementing a server "tailing" a log file for EVE alerts.
    '''
    def __init__(self, *, url: str, path: str):
        super().__init__(url=url)
        self.file_path = path

    def _wait_for_file(self):
        count = 0
        max_retries = 20
        while count < max_retries:
            if os.path.isfile(self.file_path) and os.access(self.file_path, os.R_OK):
                return
            time.sleep(5)
        log.error("cannot read file %s", self.file_path)
        sys.exit()

    def run(self):
        self._wait_for_file()

        i = inotify.adapters.Inotify()
        i.add_watch(self.file_path, mask=inotify.constants.IN_MODIFY)

        with open(self.file_path) as fd:
            fd.seek(0, 2)
            log.info("Tailing from file %s", self.file_path)
            for event in i.event_gen(yield_nones=False):
                log.debug("got inotify event %s", str(event))
                data = fd.readline().strip()
                log.debug("received data %s", str(data))
                super().alert(data)
