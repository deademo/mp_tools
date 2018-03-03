import network

from wlog import log


client = None


def connect(ssid, password):
    global client
    log('Connecting to "{}"... '.format(ssid), end='')
    client = network.WLAN(network.STA_IF)
    client.active(True)
    client.connect(ssid, password)

    while not client.isconnected():
        pass
    log('IP: {}'.format(get_ip()))
    log('done')


def get_ip():
    global client
    ip = client.ifconfig()[0]

    return ip
