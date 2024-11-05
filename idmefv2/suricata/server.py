import asyncio

class EVEServer:
    BUFFSIZE = 65536

    def __init__(self, sock_path: str, idmefv2_url: str):
        self.sock_path = sock_path
        self.idmefv2_url = idmefv2_url

    async def handle_alert(self, reader, writer):
        '''
            Handle an alert
        '''
        b = await reader.read(self.BUFFSIZE)
        print(b)

        s = str(b).upper()
        writer.write(s.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def start(self):
        '''
            Start the server listening on Unix socket specified

                Parameters:
                    sock_path(str): path to the Unix socket
        '''
        server = await asyncio.start_unix_server(self.handle_alert, self.sock_path)

        # log    print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()
