import math
strip.show([(
    int(127 + 127 * math.sin(i * 0.1)),
    int(127 + 127 * math.sin(i * 0.1 + 2)),
    int(127 + 127 * math.sin(i * 0.1 + 4))
) for i in range(144)])

# strip.off() - Turns off all the LEDs on the strip.