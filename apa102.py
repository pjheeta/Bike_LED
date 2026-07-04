from machine import SPI, Pin

class APA102:
    def __init__(self, spi_id=1, sck_pin=7, mosi_pin=9,
                 num_leds=78, brightness=31):
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