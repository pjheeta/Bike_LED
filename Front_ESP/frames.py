"""
frames.py — POV Animation Frames
==================================
Each frame is a list of NUM_COLUMNS columns.
Each column is a list of NUM_LEDS (r,g,b) tuples.

Architecture:
  4 arms x 2 faces = 8 strips x 27 LEDs = 216 total
  Daisy chain: A1→B1→A2→B2→A3→B3→A4→B4
  B faces are reversed (rim→hub) so images don't mirror.

NUM_COLUMNS = 60 angular slices per rotation.
"""

def make_arm_column(col, num_cols, leds_per_strip, reverse=False):
    """
    Generate one strip's worth of colors for a given column.
    reverse=True for B (back) face strips — flips hub/rim order.
    """
    pixels = []
    for led in range(leds_per_strip):
        hue = ((led * 360 // leds_per_strip) + (col * 360 // num_cols)) % 360
        r, g, b = hsv_to_rgb(hue)
        pixels.append((r, g, b))
    if reverse:
        pixels = list(reversed(pixels))
    return pixels

def hsv_to_rgb(h):
    h = h % 360
    if   h < 60:  return (255, int(h / 60 * 255), 0)
    elif h < 120: return (int((120 - h) / 60 * 255), 255, 0)
    elif h < 180: return (0, 255, int((h - 120) / 60 * 255))
    elif h < 240: return (0, int((240 - h) / 60 * 255), 255)
    elif h < 300: return (int((h - 240) / 60 * 255), 0, 255)
    else:         return (255, 0, int((360 - h) / 60 * 255))

def make_rainbow_frame(num_cols, num_leds):
    """
    Rolling rainbow across all 216 LEDs per column.
    Looks great from both sides of the wheel.
    """
    leds_per_strip = num_leds // 8
    frame = []
    for col in range(num_cols):
        column = []
        # 4 arms x 2 faces (A=forward, B=reversed)
        for arm in range(4):
            column += make_arm_column(col, num_cols, leds_per_strip, reverse=False)  # A face
            column += make_arm_column(col, num_cols, leds_per_strip, reverse=True)   # B face
        frame.append(column)
    return frame

def make_solid_frame(num_cols, num_leds, r, g, b):
    """All LEDs one solid color."""
    column = [(r, g, b)] * num_leds
    return [column] * num_cols

def make_cross_frame(num_cols, num_leds):
    """
    Bright cross pattern — one color per arm pair.
    Arms glow their own color, looks like a 4-color cross.
    """
    leds_per_strip = num_leds // 8
    arm_colors = [
        (255, 0,   0  ),   # Arm 1 — Red
        (0,   255, 0  ),   # Arm 2 — Green
        (0,   0,   255),   # Arm 3 — Blue
        (255, 255, 0  ),   # Arm 4 — Yellow
    ]
    frame = []
    for col in range(num_cols):
        column = []
        for arm in range(4):
            r, g, b = arm_colors[arm]
            column += [(r, g, b)] * leds_per_strip   # A face
            column += [(r, g, b)] * leds_per_strip   # B face
        frame.append(column)
    return frame

def make_test_frame(num_cols, num_leds):
    """Default frame — rolling rainbow. Used on boot."""
    return make_rainbow_frame(num_cols, num_leds)
