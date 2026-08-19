#Simple LED test without any fun stuff
#make sure main.py and apa102.py is installed on the esp32 before running this code

from machine import SPI, Pin

spi = SPI(1, baudrate=8_000_000, polarity=0, phase=0,
          sck=Pin(7), mosi=Pin(9))

def show(pixels):
    data = bytearray(4)
    for r, g, b in pixels:
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        data += bytes([0xFF, b, g, r])
    data += bytes([0xFF] * 2)
    spi.write(data)

# Rainbow across 28 LEDs
NUM_LEDS = 28
pixels = []
for i in range(NUM_LEDS):
    hue = i / NUM_LEDS
    r = int(max(0, min(1, abs(hue * 6 - 3) - 1)) * 255)
    g = int(max(0, min(1, 2 - abs(hue * 6 - 2))) * 255)
    b = int(max(0, min(1, 2 - abs(hue * 6 - 4))) * 255)
    pixels.append((r, g, b))

show(pixels)
print("Rainbow across 28 LEDs!")

# strip.off() - Turns off all the LEDs on the strip.