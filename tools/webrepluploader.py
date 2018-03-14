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

        level = logging.INFO
        self.logger = logging.getLogger('webrepluploader')
        self.logger.setLevel(level)
        self.logger.handler = []
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(ch)

    @property
    def url(self):
        return 'ws://{}:{}'.format(self.ip, self.port)

    async def connect(self):
        self.logger.info('Connecting to {}'.format(self.url))
        self.websocket = await websockets.connect(self.url, timeout=1)
        self.logger.info('Connected')

        await self.expect('Password:')

        await self.websocket.send(str(self.password).encode()+b'\n')
        await self.expect('>>>')

    async def expect(self, wait_for='>>>'):
        self.logger.debug('Receiving answer...')
        msg = ''
        while True:
            msg += await self.websocket.recv()
            if msg.strip().endswith(wait_for):
                break
        self.logger.debug('Received: {}'.format(msg))
        if wait_for and not msg.strip().endswith(str(wait_for)):
            raise RuntimeError('Not exceted output. "{}" got, but "{}" expected'.format(msg, wait_for))
        return msg

    async def write(self, data, wait_for='>>>'):
        if not isinstance(data, str):
            data = str(data)
        data += '\r\n'

        self.logger.debug('Sending: {}'.format(data.strip()))
        await self.websocket.send(data)
        await self.expect(wait_for)
                
    async def upload_file(self, file_path, file_dest=None):
        if file_dest is None:
            file_dest = os.path.basename(file_path)
        await self.write("f = open('{}', 'w+')".format(file_dest))

        file_size = os.path.getsize(file_path)
        read_size = 0
        def report():
            if report.last_sent == 0 or percent > report.last_sent + 20 or percent == 100:
                self.logger.info('[{:0.1f}%] Sending file {}'.format(percent, file_path))
                report.last_sent = percent
        report.last_sent = 0

        needed_size = 128

        with open(file_path, 'r') as f:
            _buf = ''
            for linu_number, line in enumerate(f.readlines()):
                read_size += len(line.encode())
                _buf += line

                if len(_buf) >= needed_size:
                    foo = 'f.write'
                    _buf = _buf.replace("'", "\\'")
                    _buf = _buf.strip('\n')
                    _buf = "{}('{}\\n'); ".format(foo, _buf)

                    await self.write(_buf)
                    _buf = ''

                percent = read_size/file_size*100
                report()
        await self.write("f.close()")

        percent = 100
        report()



async def main():
    ip = '192.168.1.100'
    port = 8266
    password = 1234

    client = WebREPLUploader(ip, port, password)
    await client.connect()
    await client.upload_file('../wlog.py')
    await client.websocket.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
