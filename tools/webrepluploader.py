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
        self.websocket = None

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'http://micropython.org',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8',
        }


        self.logger.info('Connecting to {}'.format(self.url))
        self.websocket = await websockets.connect(
            self.url,
            # subprotocol=['permessage-deflate', 'client_max_window_bits'],
            # extra_headers=headers
        )
        self.logger.info('Connected')

        await self.expect('Password:')

        await self.websocket.send(str(self.password).encode()+b'\n')
        await self.expect('>>>')

    async def expect(self, wait_for='>>>'):
        self.logger.debug('Receiving answer...')
        msg = ''
        while True:
            buf = await self.websocket.recv()
            msg += buf
            if buf.strip().endswith(wait_for):
                break
        self.logger.debug('Received: {}'.format(msg))
        if wait_for and not msg.strip().endswith(str(wait_for)):
            raise RuntimeError('Not exceted output. "{}" got, but "{}" expected'.format(msg, wait_for))
        return msg

    async def write(self, data, wait_for='>>>'):
        if not isinstance(data, str):
            data = str(data)
        data += '\r\n'

        self.logger.debug('Sending: {}'.format(data))
        await self.websocket.send(data)
        msg = ''
        for i in range(len(data)):
            msg += await self.websocket.recv()
            if msg.strip().endswith(wait_for):
                break
                
    async def upload_file(self, file_path, file_dest=None):
        if file_dest is None:
            file_dest = os.path.basename(file_path)
        self.write("f = open('{}', 'w+')".format(file_dest))
        with open(file_path, 'r') as f:
            for line in f.readlines():
                foo = 'f.write'
                line = line.replace("'", "\\'")
                line = line.strip('\n')
                line = "{}('{}\\n')".format(foo, line)
                self.write(line)
        self.write("f.close()")



async def main():
    ip = '192.168.1.100'
    port = 8266
    password = 1234

    client = WebREPLUploader(ip, port, password)
    await client.connect()
    await client.upload_file('../boot.py')
    await client.websocket.close()
    # msg = await client.write('open("testtest123123", "a+").close()')
    # msg = await client.write('print("112312312312312323")')
    # msg = await client.write('print("112312312312312323")')
    # msg = await client.websocket.recv()
    # await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
