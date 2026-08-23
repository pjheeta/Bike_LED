from machine import Pin
import time

class HallSync:
    def __init__(self, pin_num=4):
        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._last_trigger_us = 0   # Time of last magnet pass in microseconds
        self._period_us = 0         # Time between last two triggers in microseconds
        self.rotation_count = 0     # Total number of rotations since boot
        self._debounce_us = 5000    # 5ms debounce — ignores noise/double triggers

        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._isr)

    def _isr(self, pin):
        now = time.ticks_us()
        diff = time.ticks_diff(now, self._last_trigger_us)

        if diff < self._debounce_us:
            return  # Ignore noise

        if self._last_trigger_us != 0:
            self._period_us = diff

        self._last_trigger_us = now
        self.rotation_count += 1

    def get_period(self):
        """Returns microseconds per rotation. 0 if not yet measured."""
        return self._period_us

    def is_spinning(self):
        """Returns False if no trigger in last 1 second."""
        if self._last_trigger_us == 0:
            return False
        age = time.ticks_diff(time.ticks_us(), self._last_trigger_us)
        return age < 1_000_000

    def get_rpm(self):
        """Returns current RPM. 0 if not spinning."""
        if self._period_us == 0:
            return 0.0
        return 60_000_000 / self._period_us
