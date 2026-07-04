from machine import SPI, Pin
import time

class APA102:
    def __init__(self, spi_id=1, sck_pin=7, mosi_pin=9, num_leds=39, brightness=31):
        # brightness: 0-31, keep modest to start (full brightness draws a lot of current)
        self.num_leds = num_leds
        self.brightness = brightness & 0x1F
        self.spi = SPI(spi_id, baudrate=8_000_000, polarity=0, phase=0,
                        sck=Pin(sck_pin), mosi=Pin(mosi_pin))
        self.buf = bytearray(4 * (num_leds + 2) + (num_leds // 16 + 1))

    def show(self, pixels):
        # pixels: list of (r, g, b) tuples, length == num_leds
        data = bytearray(4)  # start frame: 0x00000000
        for r, g, b in pixels:
            data += bytes([0xE0 | self.brightness, b, g, r])
        # end frame: enough clock cycles to latch all LEDs
        data += bytes([0xFF] * ((self.num_leds // 16) + 1))
        self.spi.write(data)

    def off(self):
        self.show([(0, 0, 0)] * self.num_leds)


# Test it stand-alone first — upload this file, then in Thonny's shell run:

# pythonfrom apa102 import APA102
# strip = APA102(num_leds=39)
# strip.show([(255, 0, 0)] * 39)   # all red

# If the strip lights up solid red, your wiring and SPI config are correct. 
# If nothing happens, double check the SCK/MOSI pin numbers match your actual wiring 
# (these are the default XIAO ESP32-S3 SPI pins — confirm against the board's 
# pinout diagram, they can vary).

        