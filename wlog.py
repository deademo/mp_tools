import uasyncio as asyncio
import sys


class WirelessLogger:
    def __init__(self, host, port, loop=None):
        self.host = host
        self.port = port
        self.peer = None
        self.loop = loop or asyncio.get_event_loop()

    async def _handle(self, reader, writer):
        self.peer = writer
        print('Connected')

    def start(self):
        return asyncio.start_server(self._handle, self.host, self.port)

    async def awrite(self, message, end='\n', flush=False):
        print(message, flush=flush, end=end)
        if self.peer:
            try:
                await self.peer.awrite('{}{}'.format(message, end))
            except:
                try:
                    await self.peer.aclose()
                except:
                    pass
                self.write('Disconnected')
                self.peer = None

    def write(self, *args, **kwargs):
        asyncio.ensure_future(self.awrite(*args, **kwargs), loop=self.loop)

logger = WirelessLogger('0.0.0.0', 81)

def log(*args, **kwargs):
    logger.write(*args, **kwargs)
