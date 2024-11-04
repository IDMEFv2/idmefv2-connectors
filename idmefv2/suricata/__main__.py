
import asyncio
from idmefv2.suricata.server import EVEServer

server = EVEServer('foo', 'http://127.0.0.1:33333')
asyncio.run(server.start())
