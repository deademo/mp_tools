import uasyncio as asyncio
import sys


class WirelessLogger:
    def __init__(self, host, port, loop=None):
        self.host = host
        self.port = port
        self.peer = None
        self.loop = loop or asyncio.get_event_loop()
        self._history = []
        self._history_max_size = 1000

    async def _handle(self, reader, writer):
        self.peer = writer
        print('Connected')
        await self.awrite('', end='') # flushing history

    def start(self):
        return asyncio.start_server(self._handle, self.host, self.port)

    @property
    def history_size(self):
        return sum([len(x) for x in self._history])

    async def awrite(self, message, end='\n', flush=False, important=False):
        # wifi
        if self.peer:
            messages_to_del = []
            try:
                for i, (h_message, h_end) in list(enumerate(self._history)):
                    await self.peer.awrite('{}{}'.format(h_message, h_end))
                    messages_to_del.append(i)
                await self.peer.awrite('{}{}'.format(message, end))
            except:
                self._history.append((message, end))
                try:
                    await self.peer.aclose()
                except:
                    pass
                print('Disconnected')
                self.peer = None

            for i in sorted(messages_to_del, reverse=True):
                del self._history[i]
        else:
            if self.history_size < self._history_max_size:
                self._history.append((message, end))

        # screen
        if screen and screen.initialized:
            screen.write_line(message)

    def write(self, message, end='\n', flush=False, important=False):
        print(message, flush=flush, end=end)
        asyncio.ensure_future(self.awrite(message, end, flush, important), loop=self.loop)

logger = WirelessLogger('0.0.0.0', 81)

def log(*args, **kwargs):
    logger.write(*args, **kwargs)

# try:
#     from screen import screen
# except Exception as e:
#     log(e)
#     screen = None
screen = None