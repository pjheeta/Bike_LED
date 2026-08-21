"""
rear_test.py — Rear Wheel Battery Test
=======================================
Cycles all 40 LEDs through red → green → blue → white → repeat
Color changes every 2 seconds.

Upload this as main.py on the rear XIAO.
Also upload apa102.py.
"""

import time
from machine import SPI, Pin

# ── Config ────────────────────────────────────
NUM_LEDS = 28
BRIGHTNESS = 8        # 0-31
DELAY_MS   = 2000     # 2 seconds per color

# ── SPI setup ─────────────────────────────────
spi = SPI(1, baudrate=8_000_000, polarity=0, phase=0,
          sck=Pin(7), mosi=Pin(9))

# ── APA102/SK9822 driver ──────────────────────
def show(r, g, b):
    """Fill all LEDs with one color."""
    brightness_byte = 0xE0 | BRIGHTNESS
    data = bytearray(4)                          # start frame
    for _ in range(NUM_LEDS):
        data += bytes([brightness_byte, b, g, r])  # BGR order
    data += bytes([0xFF] * ((NUM_LEDS // 2) + 1)) # end frame
    spi.write(data)

# ── Color sequence ────────────────────────────
colors = [
    ("RED",   255, 0,   0  ),
    ("GREEN", 0,   255, 0  ),
    ("BLUE",  0,   0,   255),
    ("WHITE", 255, 255, 255),
]

print("Rear wheel battery test started — {} LEDs".format(NUM_LEDS))

i = 0
while True:
    name, r, g, b = colors[i % len(colors)]
    print("Color: {}".format(name))
    show(r, g, b)
    time.sleep_ms(DELAY_MS)
    i += 1
