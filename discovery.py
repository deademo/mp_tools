import uasyncio as asyncio
from uasyncio import core
import usocket as socket
from wlog import log


class DiscoveryServer:
    def __init__(self, local_ip, port=8282, delay=1, loop=None):
        self._socket = None
        self._local_ip = local_ip
        self._port = port
        self.loop = loop or asyncio.get_event_loop()
        self.delay = delay

    @property
    def socket(self):
        if not self._socket:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setblocking(False)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._local_ip, self._port))
        return self._socket

    def on_message(self, message):
        log('Got message: {}'.format(message))

    async def start(self):
        message = 'iamesp'
        broadcast_address = '.'.join(self._local_ip.split('.')[:-1])+'.255'

        while True:
            bytes_written_count = self.socket.sendto(message, (broadcast_address, self._port))
            # log('Broadcasting using UPD [{} bytes]: {}'.format(bytes_written_count, message))
            if len(message) != bytes_written_count:
                await asyncio.IOWrite(self.socket)
            await asyncio.sleep(self.delay)

        await self.close()

    async def close(self):
        await core.IOReadDone(self.socket)
        self.socket.close()
        self.socket = None
