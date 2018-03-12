import asyncio
import base64
import logging
import os

import websockets


class WebREPLUploader:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.logger = logging.getLogger('webrepluploader')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handler = []
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(ch)

    @property
    def url(self):
        return 'ws://{}:{}'.format(self.ip, self.port)

    async def connect(self):
        self.logger.info('Connecting to {}'.format(self.url))
        async with websockets.connect(self.url) as websocket:
            self.logger.info('Connected')

            msg = await websocket.recv()
            if msg.strip().endswith('Password:'):
                self.logger.info('Password required, sending...')
                _pass = (str(self.password)+'\n').encode()
                await websocket.send(_pass)
            else:
                raise RuntimeError('No password required')

            msg = await websocket.recv()
            if msg.strip().endswith('>>>'):
                self.logger.info('Successfuly connected')
            else:
                raise RuntimeError('Error at connecting')


async def main():
    ip = '192.168.1.100'
    port = 8266
    password = 1234

    client = WebREPLUploader(ip, port, password)
    await client.connect()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
