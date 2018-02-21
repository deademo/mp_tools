import requests


def is_alive(ip, port=80):
    try:
        return requests.get('http://{}:{}/ping'.format(ip, port), timeout=3).text == 'pong'
    except:
        return False

# print(is_alive('192.168.1.100'))

from socket import socket

class BroadcastProtocol:
    def __init__(self, loop):
        self.loop = loop
 
    def connection_made(self, transport):
        pass

# import logging
# logging.basicConfig(format='%(asctime)s %(msg)s')
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

discovered_ips = set()

def on_message(message, addr):
    global discovered_ips
    if message == b'iamesp':
        discovered_ips.add(addr[0])

import asyncio
from socket import *
loop = asyncio.get_event_loop()
ip, port = '', 82
protocol = BroadcastProtocol(loop)
protocol.datagram_received = on_message


sock = socket(AF_INET, SOCK_DGRAM)
sock.setblocking(False)

sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

sock.bind((ip, port))

transport, protocol = loop.run_until_complete(loop.create_datagram_endpoint(lambda: protocol, sock=sock))

async def test_discover():
    global discovered_ips
    print('Started discovering')
    transport.sendto(b'ping', ('255.255.255.255', 82))
    await asyncio.sleep(10)
    print('Discovered {} ips'.format(len(discovered_ips)))
    for ip in sorted(list(discovered_ips)):
        print(ip)

# loop.run_forever()
loop.run_until_complete(test_discover())
