import asyncio
import logging
import socket
import types

import requests


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s')


class DiscoveryTool:
    def __init__(self, port=82, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        self.logger = logging.getLogger('discovery')
        self.logger.setLevel(logging.DEBUG)


        self.port = port
        self._transport = None

        # It's expected delay between incoming messages
        # Needed to calculate how much time needed to wait to make sure
        # that all devices discovered
        self._expected_message_delay = 1
        self._messages_count_to_wait = 3
        self._discovered_ips_buffer = set()

    def on_message(self, message, addr):
        self.logger.debug('From {}: {}'.format(addr[0], message))
        if message == b'iamesp':
            self.logger.debug('It\'s needed message! Storing this ip.')
            self._discovered_ips_buffer.add(addr[0])

    async def listen(self):
        protocol = types.SimpleNamespace()
        protocol.datagram_received = self.on_message
        protocol.connection_made = lambda x: None

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(False)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', self.port))

        self._transport, protocol = await self.loop.create_datagram_endpoint(lambda: protocol, sock=s)
        self.logger.debug('Started listening at port {}'.format(self.port))

    async def discover(self):
        self.logger.info('Started discovering')

        # Clearing buffer for new discover session
        self._discovered_ips_buffer = set()

        # Initializing discovery communication
        # Strange point: needs to send broadcast message to start taking messages
        self._transport.sendto(b'ping', ('255.255.255.255', self.port))

        # Waiting for incoming messages
        time_to_wait = self._expected_message_delay*self._messages_count_to_wait
        self.logger.debug('Waiting {} s'.format(time_to_wait))
        await asyncio.sleep(time_to_wait)

        return self._discovered_ips_buffer

    def start(self):
        if not self.loop.is_running():
            self.loop.run_until_complete(self.astart())
        else:
            asyncio.ensure_future(self.astart(), loop=self.loop)

    async def astart(self):
        await self.listen()
        await self.discover()
        self.logger.info('Discovered {} ips'.format(len(self._discovered_ips_buffer)))
        for ip in sorted(list(self._discovered_ips_buffer)):
            self.logger.info(ip)

    #TODO: use asyncio
    def is_alive(self, ip, port=80):
        try:
            return requests.get('http://{}:{}/ping'.format(ip, port), timeout=3).text == 'pong'
        except:
            return False


if __name__ == '__main__':
    DiscoveryTool().start()