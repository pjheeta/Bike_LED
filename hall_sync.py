# *** DEFINING IMPORTS ***
# Pin — controls GPIO pins on the XIAO. Needed to read the hall sensor output.
# time — gives access to microsecond timing functions. Critical for measuring rotation speed precisely.
from machine import Pin
import time

# *** CREATING THE HALLSYNC CLASS ***
# pin_num=4 — which GPIO pin the hall sensor is connected to. 
# Default is GPIO4, but you can change it when creating the HallSync object in main.py.
class HallSync:
    def __init__(self, pin_num=4):  #takes pin number as an argument, default is 4 (GPIO4 = D3 on XIAO)
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP) #setting up the GPIO pin for the hall sensor
        # Pin(pin_num) — selects GPIO4
        # Pin.IN — sets it as an input pin (reading a signal, not sending one)
        # Pin.PULL_UP — activates the internal pull-up resistor
        self.last_time = time.ticks_us() # last_time — timestamp of the last magnet trigger in microseconds. Initialized to current time on startup
        self.period_us = 0 # period_us — how long the last full rotation took in microseconds. Starts at 0 (not spinning yet)
        self.rotation_count = 0  # rotation_count — total number of rotations detected since boot. Used by main.py to advance animation frames

        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_trigger) # Sets up a hardware interrupt
        # trigger=Pin.IRQ_FALLING — fire the interrupt on a falling edge — the moment the pin goes from HIGH (1) to LOW (0). 
        # That's exactly when the magnet passes the sensor.
        # handler=self._on_trigger — which function to call when triggered. Note no parentheses — you're passing the function itself, not calling it.
    
    # *** INTERRUPT HANDLER ***
    # This function is called automatically by the hardware interrupt whenever the hall sensor detects a magnet passing
    def _on_trigger(self, pin):
        now = time.ticks_us() # Records the exact microsecond timestamp when the trigger fired
        diff = time.ticks_diff(now, self.last_time) # Calculates how long it's been since the last trigger. time.ticks_diff handles 
        # microsecond wraparound automatically.
        if diff > 5000: 
            # Ignores any triggers that happen within 5 milliseconds of the last one. This is a debounce filter to prevent false readings 
            # from noise or multiple magnets.
            self.period_us = diff  
            # Updates the rotation period to the time since the last trigger. This is how long one full wheel rotation took in microseconds.
            self.last_time = now # Updates the timestamp for next time.
            self.rotation_count += 1 # Increments the total rotation count. This is used by main.py to advance animation frames every few rotations.


    # *** PUBLIC METHODS ***
    # get_period() — returns the last measured rotation period in microseconds. Used by main.py to calculate how long to display each 
    # column of the current frame.
    def get_period(self):
        return self.period_us
    
    
    def is_spinning(self):
        return time.ticks_diff(time.ticks_us(), self.last_time) < 1_000_000
    # is_spinning() — returns True if the wheel is spinning (i.e., a magnet has passed the sensor within the last second), or False if
    # the wheel is stationary. Used by main.py to turn off the LEDs when the bike isn't moving.

#     Test it stand-alone — upload this file, then in the shell:

# pythonfrom hall_sync import HallSync
# h = HallSync(pin_num=3)
# # wave a magnet past the sensor a few times, then:
# print(h.rotation_count, h.period_us)

# You should see the count increase and a period value in microseconds. 
# If rotation_count stays at 0, check your wiring and confirm the GPIO 
# pin number matches what you actually wired.

#strip.off() - Turns off all the LEDs on the strip.