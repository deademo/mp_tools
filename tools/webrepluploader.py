import asyncio
import base64
import logging
import os

import websockets



logger = logging.getLogger('uploader')

ip = '192.168.1.100'
port = 8266
url = 'ws://{}:{}'.format(ip, port)
password = 1234


class WebREPLUploader:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password

    @property
    def url(self):
        return 'ws://{}:{}'.format(ip, port)

    def connect(self):
        pass


async def main():

    client = WebREPLUploader(ip, port, password)
    await client.connect()

    logger.info('Connecting to {}'.format(url), flush=True)

    async with websockets.connect(url) as websocket:
        logger.info('Connected')

        msg = await websocket.recv()
        if msg.strip().endswith('Password:'):
            logger.info('Password required, sending')
            _pass = (str(password)+'\n').encode()
            await websocket.send(_pass)
        else:
            raise RuntimeError('No password required')

        msg = await websocket.recv()
        if msg.strip().endswith('>>>'):
            logger.info('Successfuly connected')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
