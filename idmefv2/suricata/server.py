'''
    The Unix socket server listening for EVE alerts
'''
import asyncio
import json
import logging
import textwrap
import aiohttp

class EVEServer:
    '''
        A class implementing an asyncio server listening on a Unix socket for EVE alerts.
        On receiving an alert, convert it to IDMEFv2 and send it to a IDMEFv2 HTTPS server
    '''
    BUFFSIZE = 65536

    def __init__(self, socket_path: str, idmefv2_url: str):
        '''

            Parameters:
                socket_path(str): path to the Unix socket
                idmefv2_url(str): the url of the IDMEFv2 HTTPS server
        '''
        self.socket_path = socket_path
        self.idmefv2_url = idmefv2_url
        self.session = None

    async def handle_alert(self, reader, writer):
        '''
            Handle an alert
        '''
        b = await reader.read(self.BUFFSIZE)

        logging.debug("received alert %s", textwrap.shorten(str(b), 128))

        alert = json.loads(b)

        await self.session.post(self.idmefv2_url, json=alert)

        writer.close()
        await writer.wait_closed()

    async def start(self):
        '''
            Start the server listening on Unix socket specified in constructor.
        '''
        server = await asyncio.start_unix_server(self.handle_alert, self.socket_path)

        self.session = aiohttp.ClientSession()

        logging.info("Listening on Unix socket %s", self.socket_path)

        await server.serve_forever()
        await self.session.close()
        logging.info('Server closed')
