import uselect as select
import usocket as socket
import network
import machine
from machine import Timer
try:
    from settings_local import WIFI_SSID, WIFI_PASSWORD
except:
    from settings import WIFI_SSID, WIFI_PASSWORD

try:
    import wifi
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    ip = wifi.get_ip()
except:

    client = network.WLAN(network.STA_IF)
    client.active(True)
    client.connect(WIFI_SSID, WIFI_PASSWORD)
    while not client.isconnected():
        pass
    ip = client.ifconfig()[0]

print('IP: {}'.format(ip))
import webrepl
webrepl.start()
