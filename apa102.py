# For 144 LED/meter
# Front Wheel has 72 LEDS (36 on each side)
# For 30 LED/meter
# 10" Spokes has 14 LEDs (7/side)
# NUM_LEDS is defined in main.py and passed to this class — only change it there

# *** LOADS ALL THE LIBRARIES NEEDED ***
# Loads the micropython machine module
# SPI is for the SPI bus, Pin is for the GPIO pins
from machine import SPI, Pin


# *** CREATING THE APA102 CLASS ***
# spi_id=1 — which SPI bus to use. The XIAO ESP32-S3 has two SPI buses (0 and 1). We use bus 1.
# sck_pin=7 — which GPIO pin is the clock (yellow wire / CI). GPIO7 = D8 on XIAO.
# mosi_pin=9 — which GPIO pin is the data (green wire / DI). GPIO9 = D10 on XIAO.
# num_leds — how many LEDs in the chain. No default — must be passed from main.py via NUM_LEDS.
# brightness=31 — global brightness, 0-31. 31 is maximum.
class APA102:
    def __init__(self, spi_id=1, sck_pin=7, mosi_pin=9,
                 num_leds=None, brightness=31):
        self.num_leds = num_leds  # Received from main.py
        self.brightness = brightness & 0x1F
        # 0x1F in binary is 00011111 — forces brightness to stay within 0-31
        # even if someone accidentally passes a higher value. Safety clamp.

        # *** SPI SETTINGS ***
        # spi_id — which bus (1)
        # baudrate=8_000_000 — data speed: 8 million bits per second. SK9822 can handle up to 40MHz — we're well within spec.
        # polarity=0 — clock starts LOW. This is part of the SPI "mode" setting.
        # phase=0 — data is read on the rising edge of the clock. Together with polarity=0, this is SPI Mode 0 which is what SK9822 requires.
        # sck=Pin(sck_pin) — assigns GPIO7 as the clock pin
        # mosi=Pin(mosi_pin) — assigns GPIO9 as the data pin. MOSI stands for Master Out Slave In — data flows FROM the XIAO TO the LEDs.
        self.spi = SPI(spi_id, baudrate=8_000_000,
                       polarity=0, phase=0,
                       sck=Pin(sck_pin), mosi=Pin(mosi_pin))


    # *** METHOD THAT SENDS COLOR DATA TO THE LEDS ***
    def show(self, pixels):
        data = bytearray(4)  # Creates 4 zero bytes [0x00, 0x00, 0x00, 0x00]. This is the start frame — signals "new data coming"
        for r, g, b in pixels:  # Each pixel is a tuple of (r, g, b) values. The for loop unpacks the tuple into r, g, b variables.
            data += bytes([0xE0 | self.brightness, b, g, r])
            # The APA102 protocol requires a 4-byte frame for each LED:
            # Byte 1: 0xE0 | brightness — "global brightness" byte. 0xE0 = 11100000 in binary.
            #         The | (OR) combines it with brightness (0-31) to form 111xxxxx.
            #         At full brightness (31 = 00011111) this becomes 11111111 = 0xFF.
            # Byte 2: b — blue value (0-255)
            # Byte 3: g — green value (0-255)
            # Byte 4: r — red value (0-255)
            # NOTE: order is B, G, R not R, G, B — SK9822 expects blue first!
        data += bytes([0xFF] * ((self.num_leds // 16) + 1))
        # End frame — required by APA102 protocol to signal end of data.
        # Formula (num_leds // 16) + 1 calculates how many 0xFF bytes are needed.
        # More LEDs in the chain = more end bytes needed to clock signal to the last LED.
        # Example: 14 LEDs → (14 // 16) + 1 = 1 byte. 72 LEDs → (72 // 16) + 1 = 5 bytes.
        self.spi.write(data)  # Blasts the entire byte array out over SPI in one shot.
        # At 8MHz, 72 LEDs worth of data takes about 288 microseconds — effectively instant.


    # *** METHOD THAT TURNS OFF ALL THE LEDS ***
    def off(self):
        self.show([(0, 0, 0)] * self.num_leds)
        # Black = (0, 0, 0) = no light = LEDs off.
        # Reuses show() rather than duplicating code.
