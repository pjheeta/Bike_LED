import time
from apa102 import APA102
from hall_sync import HallSync
from frames import FRAMES, NUM_COLUMNS, NUM_LEDS

strip = APA102(num_leds=NUM_LEDS, brightness=20)
hall = HallSync(pin_num=3)

current_frame = 0
rotation_count_at_last_frame = 0
ROTATIONS_PER_FRAME = 5

while True:
    if not hall.is_spinning():
        strip.off()
        time.sleep_ms(50)
        continue

    period = hall.get_period()
    if period == 0:
        time.sleep_ms(10)
        continue

    # advance animation frame every N rotations
    if hall.rotation_count - rotation_count_at_last_frame >= ROTATIONS_PER_FRAME:
        current_frame = (current_frame + 1) % len(FRAMES)
        rotation_count_at_last_frame = hall.rotation_count

    column_duration_us = period // NUM_COLUMNS
    frame = FRAMES[current_frame]

    for col in range(NUM_COLUMNS):
        start = time.ticks_us()
        strip.show(frame[col])
        # sleep for the remaining time in this column's slot
        elapsed = time.ticks_diff(time.ticks_us(), start)
        remaining = column_duration_us - elapsed
        if remaining > 0:
            time.sleep_us(remaining)


# A few notes on this loop:

# It checks is_spinning() first so the LEDs turn off automatically when the 
# bike is parked — saves battery

# It subtracts the SPI write time (elapsed) from the sleep so columns stay 
# evenly spaced even though strip.show() itself takes nonzero time

# ROTATIONS_PER_FRAME controls animation speed — lower number = faster 
# cycling between frames