# For 144 LED/meter
# Front Wheel has 78 LEDS (39 on each side)
# Back Wheel / Test Wheel has 72 LEDs (36 on each side)
# For 30 LED/meter
# 10" Spokes has 14 LEDs (7/side)

from machine import SPI, Pin

class APA102:
    def __init__(self, spi_id=1, sck_pin=7, mosi_pin=9,
                 num_leds=14, brightness=31):
        #CHANGE LED Length here
        self.num_leds = num_leds
        self.brightness = brightness & 0x1F
        self.spi = SPI(spi_id, baudrate=8_000_000,
                       polarity=0, phase=0,
                       sck=Pin(sck_pin), mosi=Pin(mosi_pin))

    def show(self, pixels):
        data = bytearray(4)
        for r, g, b in pixels:
            data += bytes([0xE0 | self.brightness, b, g, r])
        data += bytes([0xFF] * ((self.num_leds // 16) + 1))
        self.spi.write(data)

    def off(self):
        self.show([(0, 0, 0)] * self.num_leds)