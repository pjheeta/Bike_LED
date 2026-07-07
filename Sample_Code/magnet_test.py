from machine import Pin
import time

sensor = Pin(4, Pin.IN, Pin.PULL_UP)
while True:
    print(sensor.value())
    time.sleep_ms(200)