import machine
import ssd1306
from wlog import log


D5 = 14
D2 = 4
D3 = 0
D1 = 5


class DeviceScreen:
    def __init__(self):
    
        self.oled = None
        try:
            i2c = machine.I2C(
                scl=machine.Pin(D2, machine.Pin.OUT),
                sda=machine.Pin(D1, machine.Pin.OUT),
            )
            self.oled = ssd1306.SSD1306_I2C(128, 64, i2c, 0x3c)

            self.oled.fill(0)
            self.oled.text('Initialized!', 0, 0)
            self.oled.show()
        except:
            log('Error: display not initialized')
            return

        self.initialized = self.oled is not None


    def write_line(self, str):
        if self.initialized:
            self.oled.scroll(0, 8)
            self.oled.fill_rect(0, 0, 9999, 8, 0)
            self.oled.text(message, 0, 0)
            self.oled.show()


screen = DeviceScreen()
