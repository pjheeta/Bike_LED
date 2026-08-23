import time
from apa102 import APA102

NUM_LEDS = 19
#final strip is 216 LEDs
#Test strip is 19 LEDs

strip = APA102(num_leds=NUM_LEDS, brightness=8)

def hsv_to_rgb(h):
    h = h % 360
    c = 255
    x = int(c * (1 - abs((h / 60) % 2 - 1)))
    if   h < 60:  return (c, x, 0)
    elif h < 120: return (x, c, 0)
    elif h < 180: return (0, c, x)
    elif h < 240: return (0, x, c)
    elif h < 300: return (x, 0, c)
    else:         return (c, 0, x)

def rainbow():
    pixels = []
    for i in range(NUM_LEDS):
        pixels.append(hsv_to_rgb(i * 360 // NUM_LEDS))
    return pixels

while True:
    print("RED")
    strip.show([(255, 0, 0)] * NUM_LEDS)
    time.sleep(2)

    print("GREEN")
    strip.show([(0, 255, 0)] * NUM_LEDS)
    time.sleep(2)

    print("BLUE")
    strip.show([(0, 0, 255)] * NUM_LEDS)
    time.sleep(2)

    print("WHITE")
    strip.show([(255, 255, 255)] * NUM_LEDS)
    time.sleep(2)

    print("RAINBOW")
    strip.show(rainbow())
    time.sleep(2)
