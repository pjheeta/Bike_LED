from machine import SPI, Pin

spi = SPI(1, baudrate=8_000_000, polarity=0, phase=0,
          sck=Pin(7), mosi=Pin(9))

def show(pixels):
    data = bytearray(4)
    for r, g, b in pixels:
        data += bytes([0xFF, b, g, r])
    data += bytes([0xFF] * 2)
    spi.write(data)

# Rainbow - different color per LED
show([(255,0,0),(255,128,0),(255,255,0),(0,255,0),(0,255,128),
      (0,0,255),(128,0,255),(255,0,255),(255,0,128),(255,255,255)])
print("Look at that Rainbow!")

# strip.off() - Turns off all the LEDs on the strip.