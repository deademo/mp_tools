# Change it to your wifi ssid and password
WIFI_SSID = 'CHANGE_ME'
WIFI_PASSWORD = 'CHANGE_ME'

try:
    from settings_local import *
except ImportError:
    pass
