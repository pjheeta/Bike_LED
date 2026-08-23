"""
main.py — Rear Wheel XIAO
===========================
- 40 LEDs ambient glow (4 bars x ~10 LEDs)
- Reacts to RPM data from front XIAO via ESP-NOW
- No hall sensor on rear wheel

Upload these files to rear XIAO:
  main.py, apa102.py, espnow_rx.py

Behavior:
  Not spinning  → slow random color drift
  RPM < 20      → calm pulsing rainbow
  RPM 20-60     → faster rainbow
  RPM > 60      → fast color strobe
"""

import time
import random
from apa102 import APA102
from espnow_rx import ESPNowReceiver

# ── Config ────────────────────────────────────────────────────────────────────
NUM_LEDS   = 40
BRIGHTNESS = 8

# ── Hardware ──────────────────────────────────────────────────────────────────
strip = APA102(num_leds=NUM_LEDS, brightness=BRIGHTNESS)
rx    = ESPNowReceiver()

# ── Color helper ──────────────────────────────────────────────────────────────
def hsv_to_rgb(h):
    h = h % 360
    if   h < 60:  return (255, int(h / 60 * 255), 0)
    elif h < 120: return (int((120 - h) / 60 * 255), 255, 0)
    elif h < 180: return (0, 255, int((h - 120) / 60 * 255))
    elif h < 240: return (0, int((240 - h) / 60 * 255), 255)
    elif h < 300: return (int((h - 240) / 60 * 255), 0, 255)
    else:         return (255, 0, int((360 - h) / 60 * 255))

# ── Display modes ─────────────────────────────────────────────────────────────

# Slow drift — not spinning
drift_hues    = [random.randint(0, 359) for _ in range(NUM_LEDS)]
drift_targets = [random.randint(0, 359) for _ in range(NUM_LEDS)]

def slow_drift():
    for i in range(NUM_LEDS):
        diff = drift_targets[i] - drift_hues[i]
        if abs(diff) > 180:
            diff -= 360 if diff > 0 else -360
        drift_hues[i] += 0.5 if diff > 0 else -0.5
        if abs(drift_targets[i] - drift_hues[i]) < 1:
            drift_targets[i] = random.randint(0, 359)
    strip.show([hsv_to_rgb(h) for h in drift_hues])
    time.sleep_ms(30)

# Pulsing rainbow — slow/medium riding
rainbow_offset = 0
def pulse_rainbow(rpm):
    global rainbow_offset
    shift = max(1, int(rpm / 10))
    pixels = [hsv_to_rgb((rainbow_offset + i * (360 // NUM_LEDS)) % 360) for i in range(NUM_LEDS)]
    strip.show(pixels)
    rainbow_offset = (rainbow_offset + shift) % 360
    time.sleep_ms(max(5, 50 - int(rpm / 2)))

# Fast strobe — high RPM
strobe_hue    = 0
strobe_toggle = False
strobe_frame  = 0
def fast_strobe(rpm):
    global strobe_hue, strobe_toggle, strobe_frame
    strobe_frame += 1
    if strobe_frame % 60 == 0:
        strobe_hue = random.randint(0, 359)
    h = strobe_hue if strobe_toggle else (strobe_hue + 180) % 360
    r, g, b = hsv_to_rgb(h)
    strip.show([(r, g, b)] * NUM_LEDS)
    strobe_toggle = not strobe_toggle
    time.sleep_ms(max(20, 100 - int(rpm)))

# ── Main loop ─────────────────────────────────────────────────────────────────
print('Rear wheel started —', NUM_LEDS, 'LEDs')

while True:
    rx.poll()
    data = rx.get_latest()
    rpm         = data["rpm"]
    is_spinning = data["is_spinning"]

    if not is_spinning or rpm < 20:
        slow_drift()
    elif rpm < 60:
        pulse_rainbow(rpm)
    else:
        fast_strobe(rpm)
