from machine import Pin
import time

class HallSync:
    def __init__(self, pin_num=3):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.last_time = time.ticks_us()
        self.period_us = 0          # time for one full rotation
        self.rotation_count = 0
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_trigger)

    def _on_trigger(self, pin):
        now = time.ticks_us()
        diff = time.ticks_diff(now, self.last_time)
        # debounce: ignore triggers faster than 5ms (false retriggers)
        if diff > 5000:
            self.period_us = diff
            self.last_time = now
            self.rotation_count += 1

    def get_period(self):
        return self.period_us

    def is_spinning(self):
        # if no trigger in the last 1 second, treat the wheel as stopped
        return time.ticks_diff(time.ticks_us(), self.last_time) < 1_000_000
    

#     Test it stand-alone — upload this file, then in the shell:

# pythonfrom hall_sync import HallSync
# h = HallSync(pin_num=3)
# # wave a magnet past the sensor a few times, then:
# print(h.rotation_count, h.period_us)

# You should see the count increase and a period value in microseconds. 
# If rotation_count stays at 0, check your wiring and confirm the GPIO 
# pin number matches what you actually wired.