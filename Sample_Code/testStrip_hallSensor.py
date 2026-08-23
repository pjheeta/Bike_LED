#Save this on the ESP32S3 as main.py
from machine import SPI, Pin
import time

hall = Pin(4, Pin.IN, Pin.PULL_UP)
spi = SPI(1, baudrate=8_000_000, polarity=0, phase=0, sck=Pin(7), mosi=Pin(9))

NUM_LEDS = 216
#final strip is 216 LEDs
#Test strip is 19 LEDs


def show(r, g, b, n=NUM_LEDS):
    data = bytearray(4)
    for i in range(n):
        data += bytes([0xE8, b, g, r])
    data += bytes([0xFF] * ((n // 16) + 1))
    spi.write(data)

while True:
    if hall.value() == 0:  # Magnet detected
        show(0, 255, 0)    # Green when magnet passes
    else:
        show(255, 0, 0)    # Red normally
    time.sleep_ms(10)