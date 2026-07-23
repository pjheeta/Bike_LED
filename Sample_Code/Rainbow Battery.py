## Rainbow_LED strip testing batter
from apa102 import APA102
import time

strip = APA102(num_leds=7, brightness=31)

COLORS = [
    (255, 0, 0),
    (255, 128, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 255, 128),
    (0, 0, 255),
    (128, 0, 255),
]

while True:
    for offset in range(7):
        pixels = [COLORS[(i + offset) % 7] for i in range(7)]
        strip.show(pixels)
        time.sleep_ms(100)