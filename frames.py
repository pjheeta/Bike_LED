NUM_COLUMNS = 60     # angular slices per rotation
NUM_LEDS = 39         # LEDs per arm

def make_test_frame():
    # alternating red/blue columns, just to visually confirm timing
    frame = []
    for col in range(NUM_COLUMNS):
        color = (255, 0, 0) if col % 2 == 0 else (0, 0, 255)
        frame.append([color] * NUM_LEDS)
    return frame

FRAMES = [make_test_frame()]