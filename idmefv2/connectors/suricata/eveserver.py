'''
    The Unix socket server listening for EVE alerts
'''
import abc
import json
import logging
import socketserver
from typing import Union
import requests
from idmefv2.connectors.suricata.suricataconverter import SuricataConverter

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
            requests.post(self.idmefv2_url, json=idmefv2_alert, timeout=1.0)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

class EVEStreamRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        logging.debug("received data %s", str(data))
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
            logging.info("Listening on Unix socket %s", self.socket_path)
            server.serve_forever()

        logging.info('Server closed')

class EVEFileServer(EVEServer):
    '''
        A class implementing an asyncio server "tailing" a log file for EVE alerts.
    '''
    def __init__(self, *, url: str, path: str):
        super().__init__(url=url)
        self.file_path = path

    def run(self):
        while True:
            pass
