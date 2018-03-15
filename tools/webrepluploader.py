import asyncio
import base64
import logging
import os

import websockets


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s')


class WebREPLUploader:
    def __init__(self, ip, port=8266, password=1234):
        self.ip = ip
        self.port = port
        self.password = password
        self.websocket = None

        self.logger = logging.getLogger('webrepluploader')
        self.logger.setLevel(logging.WARNING)

        self.print_percent_inline = False

    @property
    def url(self):
        return 'ws://{}:{}'.format(self.ip, self.port)

    async def connect(self, tries=4):
        self.logger.info('Connecting to {}'.format(self.url))
        for i in range(tries):
            try:
                self.websocket = await websockets.connect(self.url, timeout=1)
                break
            except ConnectionRefusedError:
                self.logger.info('Connection failed, reconnecting #{}'.format(i+1))
                if i+1 >= tries:
                    raise
                await asyncio.sleep(i*2)
        self.logger.debug('Connected')

        await self.expect('Password:')

        await self.websocket.send(str(self.password).encode()+b'\n')
        await self.expect('>>>')

    async def expect(self, wait_for='>>>'):
        if wait_for is None:
            return True
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

        file_size = os.path.getsize(file_path)
        read_size = 0

        def _report():
            if report.last_sent == 0 or percent > report.last_sent + 20 or percent == 100:
                self.logger.info('[{:0.1f}%] Sending file {}'.format(percent, file_path))
                report.last_sent = percent

        if self.print_percent_inline:
            def report():
                _report()
                if report.last_sent == 0 or percent > report.last_sent + 5 or percent == 100:
                    print('\r[{:>6.2f}%] Uploading file "{}"...'.format(percent, file_path), end='', flush=True)
        else:
            report = _report

        report.last_sent = 0
        percent = 0
        needed_size = 128

        with open(file_path, 'r') as f:
            data = '\\n'.join([line.strip('\n').replace('\\n', '\\\\n').replace("'", "\\'") for line in f.readlines()])
        data_list = [data[i:i+needed_size] for i in range(0, len(data), needed_size)]
        for i in range(len(data_list)-1):
            if data_list[i].endswith('\\') and data_list[i+1][0] in ("'", "n"):
                data_list[i] = data_list[i]+data_list[i+1][0]
                data_list[i+1] = data_list[i+1][1:]

        await self.write("f = open('{}', 'w+')".format(file_dest))
        for i, buf in enumerate(data_list):
            report()
            percent = i+1/len(data_list)*100
            await self.write("f.write('{}')".format(buf))
        await self.write("f.close()")

        percent = 100
        report()

    async def close(self):
        self.logger.info('Closing connection to {}'.format(self.ip))
        await self.websocket.close()
        self.logger.debug('Closed')

    async def restart(self):
        await self.write('import machine; machine.reset()', wait_for=None)


async def upload(ip, files, port=8266, password=1234, client=None):
    if not isinstance(files, (tuple, list, set)) or isinstance(files, str):
        files = [files]
    if not client:
        _client = WebREPLUploader(ip, port, password)
        await _client.connect()
    else:
        _client = client
    for file in files:
        await _client.upload_file(file)
    if not client:
        await _client.close()


async def main():
    ip = '192.168.1.100'
    await upload(ip, ['../wlog.py', '../app.py'])


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
