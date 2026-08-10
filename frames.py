# *** FRAMES.PY ***
# This file contains all the animation frame data for the POV wheel display.
# It is imported by main.py which owns NUM_LEDS and NUM_COLUMNS.
# As you add more animations (circle, square, cross, rainbow), add them here.
# main.py never needs to know what the images look like — it just loops through FRAMES.

# *** HOW A FRAME WORKS ***
# The wheel rotation is divided into NUM_COLUMNS equal slices (like cutting a pie).
# Each slice gets one column of LED colors displayed for a precise amount of time.
# A frame is a 2D grid: NUM_COLUMNS wide × NUM_LEDS tall.
# With 4 arms, each arm flashes 4 times per rotation — much more visible at playa speeds.
#
# Visualized as a flat grid (test frame example):
#
#          Col0  Col1  Col2  Col3 ... Col59
# LED 0  [  R     B     R     B  ...   B  ]  ← hub end of arm
# LED 1  [  R     B     R     B  ...   B  ]
# ...
# LED 26 [  R     B     R     B  ...   B  ]  ← rim end of arm (front face)
# LED 27 [  B     R     B     R  ...   R  ]  ← rim end of arm (back face — reversed)
# ...
# LED 53 [  B     R     B     R  ...   R  ]  ← hub end of back face
#
# When spinning at 60 RPM your eye sees:
# 🔴🔵🔴🔵🔴🔵🔴🔵 ← floating red/blue stripes in mid-air

# *** ARM AND STRIP ARCHITECTURE ***
# 4 arms at 90° apart, each arm has front (A) and back (B) face strip
# 27 LEDs per strip × 8 strips = 216 LEDs total
#
# Strip layout per arm:
# A (front face): LEDs run hub → rim
# B (back face):  LEDs run rim → hub — REVERSED in firmware
#
# Full daisy chain:
# XIAO → A1(1-27) → B1(28-54) → A2(55-81) → B2(82-108)
#       → A3(109-135) → B3(136-162) → A4(163-189) → B4(190-216)

# *** IMPORTANT NOTE ON BACK FACE LEDS ***
# The arm has LEDs on BOTH faces (front and back).
# Front face LEDs run hub → rim (LED 0 = hub, LED 26 = rim)
# Back face LEDs run rim → hub (LED 27 = rim, LED 53 = hub) — REVERSED direction
# So back face columns must be reversed to show the image the right way up on both sides.
# This is handled automatically in every frame function below.


# *** HELPER FUNCTION ***
# Builds one column for a single arm (front + back faces combined)
# front_col = list of colors for front face (hub to rim)
# back face is automatically reversed
def make_arm_column(front_col):
    # front_col: hub → rim
    # back_col:  rim → hub (reversed so image reads correctly from both sides)
    back_col = list(reversed(front_col))
    return front_col + back_col  # Combined: 27 front + 27 back = 54 LEDs per arm


# *** TEST FRAME ***
# Creates a simple alternating red/blue stripe pattern.
# Used to visually confirm POV timing is working correctly —
# if stripes are stable and evenly spaced, timing is good.
def make_test_frame(num_columns, num_leds):
    # num_columns — how many vertical slices per rotation (passed from main.py)
    # num_leds — total LEDs in chain including all arms and faces (passed from main.py)

    leds_per_strip = num_leds // 8   # 216 // 8 = 27 LEDs per strip
    frame = []                        # Will hold num_columns lists

    for col in range(num_columns):
        # col % 2 gives remainder when dividing by 2:
        # Even columns (0, 2, 4...) → 0 → RED
        # Odd columns  (1, 3, 5...) → 1 → BLUE
        color = (255, 0, 0) if col % 2 == 0 else (0, 0, 255)

        # Build one arm column (front + back face)
        arm_col = make_arm_column([color] * leds_per_strip)

        # All 4 arms show same pattern — concatenate 4 arm columns
        full_col = arm_col * 4  # 54 LEDs × 4 arms = 216 LEDs

        frame.append(full_col)

    return frame  # Returns list of num_columns columns, each num_leds colors long


# *** CIRCLE FRAME ***
# Draws a circle/ring shape — looks great at playa speeds
# Symmetric front/back — no mirror issue
def make_circle_frame(num_columns, num_leds):
    import math
    leds_per_strip = num_leds // 8
    frame = []

    for col in range(num_columns):
        # Map column to angle (0 to 2π)
        angle = (col / num_columns) * 2 * math.pi

        # Build front face column
        front_col = []
        for led in range(leds_per_strip):
            # Map LED position to radius (0 = hub, 1 = rim)
            r = led / (leds_per_strip - 1)
            # Circle at radius 0.7 with thickness 0.15
            if abs(r - 0.7) < 0.15:
                front_col.append((0, 200, 255))  # Cyan circle
            else:
                front_col.append((0, 0, 0))      # Black (off)

        arm_col = make_arm_column(front_col)
        full_col = arm_col * 4
        frame.append(full_col)

    return frame


# *** SQUARE FRAME ***
# Draws a square shape — symmetric, looks great from both sides
def make_square_frame(num_columns, num_leds):
    leds_per_strip = num_leds // 8
    frame = []

    for col in range(num_columns):
        # Map column to position (-1 to 1) in X axis
        x = (col / num_columns) * 2 - 1  # -1 to +1

        front_col = []
        for led in range(leds_per_strip):
            # Map LED to position (-1 to 1) in Y axis
            y = (led / (leds_per_strip - 1)) * 2 - 1  # -1 to +1

            # Square boundary — draw edges only
            on_edge = (
                (abs(x) > 0.6 and abs(y) < 0.65) or
                (abs(y) > 0.6 and abs(x) < 0.65)
            )
            if on_edge:
                front_col.append((255, 100, 0))  # Orange square
            else:
                front_col.append((0, 0, 0))

        arm_col = make_arm_column(front_col)
        full_col = arm_col * 4
        frame.append(full_col)

    return frame


# *** CROSS FRAME ***
# Draws a plus/cross shape — symmetric, very visible at playa speeds
def make_cross_frame(num_columns, num_leds):
    leds_per_strip = num_leds // 8
    frame = []

    for col in range(num_columns):
        x = (col / num_columns) * 2 - 1  # -1 to +1

        front_col = []
        for led in range(leds_per_strip):
            y = (led / (leds_per_strip - 1)) * 2 - 1  # -1 to +1

            # Cross: vertical bar OR horizontal bar
            on_cross = (abs(x) < 0.15) or (abs(y) < 0.15)
            if on_cross:
                front_col.append((255, 0, 100))  # Pink cross
            else:
                front_col.append((0, 0, 0))

        arm_col = make_arm_column(front_col)
        full_col = arm_col * 4
        frame.append(full_col)

    return frame


# *** RAINBOW FRAME ***
# Full rainbow across all LEDs — great ambient effect at any speed
def make_rainbow_frame(num_columns, num_leds):
    leds_per_strip = num_leds // 8
    frame = []

    COLORS = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211),  # Violet
    ]

    for col in range(num_columns):
        # Shift colors based on column — creates spinning rainbow effect
        front_col = []
        for led in range(leds_per_strip):
            color_idx = (led + col) % len(COLORS)
            front_col.append(COLORS[color_idx])

        arm_col = make_arm_column(front_col)
        full_col = arm_col * 4
        frame.append(full_col)

    return frame


# *** FRAMES LIST ***
# All animation frames — main.py cycles through them every ROTATIONS_PER_FRAME rotations.
# Add or remove frames here as needed.
# NOTE: NUM_COLUMNS and NUM_LEDS are passed in from main.py — not defined here.
# main.py is the single source of truth for those values.
