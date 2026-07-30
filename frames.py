# *** FRAMES.PY ***
# This file contains all the animation frame data for the POV wheel display.
# It is imported by main.py which owns NUM_LEDS and NUM_COLUMNS.
# As you add more animations (Nyan Cat, polka dots, Joe's face), add them here.
# main.py never needs to know what the images look like — it just loops through FRAMES.

# *** HOW A FRAME WORKS ***
# The wheel rotation is divided into NUM_COLUMNS equal slices (like cutting a pie).
# Each slice gets one column of LED colors displayed for a precise amount of time.
# A frame is a 2D grid: NUM_COLUMNS wide × NUM_LEDS tall.
# When spinning, your eye stitches all 60 flashes into one floating image.
#
# Visualized as a flat grid (test frame example):
#
#          Col0  Col1  Col2  Col3 ... Col59
# LED 0  [  R     B     R     B  ...   B  ]  ← rim end of arm
# LED 1  [  R     B     R     B  ...   B  ]
# ...
# LED N  [  R     B     R     B  ...   B  ]  ← hub end of arm
#
# When spinning at 60+ RPM your eye sees:
# 🔴🔵🔴🔵🔴🔵🔴🔵 ← floating red/blue stripes in mid-air


# *** IMPORTANT NOTE ON BACK FACE LEDS ***
# The arm has LEDs on BOTH faces (front and back).
# Front face LEDs run hub → rim (LED 0 = hub, LED N = rim)
# Back face LEDs run rim → hub (LED 0 = rim, LED N = hub) — REVERSED direction
# So back face columns must be reversed to show the image the right way up on both sides.
# This is handled in make_frame() below.


# *** TEST FRAME ***
# Creates a simple alternating red/blue stripe pattern.
# Used to visually confirm POV timing is working correctly —
# if stripes are stable and evenly spaced, timing is good.

def make_test_frame(num_columns, num_leds):
    # num_columns — how many vertical slices per rotation (passed from main.py)
    # num_leds — total LEDs in chain including both faces (passed from main.py)

    frame = []  # Will hold num_columns lists, each containing num_leds color tuples

    for col in range(num_columns):
        # col % 2 gives remainder when dividing by 2:
        # Even columns (0, 2, 4...) → 0 → RED
        # Odd columns  (1, 3, 5...) → 1 → BLUE
        color = (255, 0, 0) if col % 2 == 0 else (0, 0, 255)

        half = num_leds // 2  # Split total LEDs into front face and back face halves

        front = [color] * half              # Front face: all same color hub → rim
        back = list(reversed([color] * half))  # Back face: reversed so image reads correctly rim → hub

        frame.append(front + back)  # Combine into one column of num_leds colors

    return frame  # Returns list of num_columns columns, each num_leds colors long


# *** FRAMES LIST ***
# All animation frames go here.
# main.py imports this and cycles through them every ROTATIONS_PER_FRAME rotations.
# Add more frames as you build them:
#
# from frames import FRAMES
# FRAMES = [
#     make_test_frame(NUM_COLUMNS, NUM_LEDS),   # frame 0 — red/blue test
#     make_nyan_cat(NUM_COLUMNS, NUM_LEDS),      # frame 1 — Nyan Cat
#     make_polka_dot(NUM_COLUMNS, NUM_LEDS),     # frame 2 — polka dots
#     make_joes_face(NUM_COLUMNS, NUM_LEDS),     # frame 3 — Joe's face
# ]
#
# NOTE: NUM_COLUMNS and NUM_LEDS are passed in from main.py — not defined here.
# main.py is the single source of truth for those values.
