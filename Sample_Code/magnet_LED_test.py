from apa102 import APA102
from machine import Pin
import time

strip = APA102(num_leds=10, brightness=31)
sensor = Pin(4, Pin.IN, Pin.PULL_UP)

RAINBOW = [
    (255, 0, 0),
    (255, 128, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 255, 128),
    (0, 0, 255),
    (128, 0, 255),
    (255, 0, 255),
    (255, 0, 128),
    (255, 255, 255)
]

last = 1
while True:
    val = sensor.value()
    if val == 0 and last == 1:
        strip.show(RAINBOW)
        time.sleep_ms(500)
        strip.off()
    last = val
    time.sleep_ms(10)