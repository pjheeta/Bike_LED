# run this on your laptop with regular Python (not MicroPython)
# requires: pip install pillow

# Once the solid-color test works, here's how to turn an actual picture 
# into FRAMES data. This part runs on your laptop, not the XIAO — you 
# generate a Python file and then upload the result.


from PIL import Image

NUM_COLUMNS = 60
NUM_LEDS = 39

def image_to_frame(path):
    img = Image.open(path).convert("RGB")
    img = img.resize((NUM_COLUMNS, NUM_LEDS))
    frame = []
    for col in range(NUM_COLUMNS):
        column_pixels = []
        for led in range(NUM_LEDS):
            r, g, b = img.getpixel((col, led))
            column_pixels.append((r, g, b))
        frame.append(column_pixels)
    return frame

def write_frames_file(image_paths, output_path="frames.py"):
    with open(output_path, "w") as f:
        f.write(f"NUM_COLUMNS = {NUM_COLUMNS}\n")
        f.write(f"NUM_LEDS = {NUM_LEDS}\n\n")
        f.write("FRAMES = [\n")
        for path in image_paths:
            frame = image_to_frame(path)
            f.write("    " + repr(frame) + ",\n")
        f.write("]\n")

# example usage:
write_frames_file(["logo.png"])


# This produces a new frames.py with your actual artwork baked in as raw pixel 
# data. Design your source image at 60 x 39 pixels (matching NUM_COLUMNS x NUM_LEDS) 
# in any image editor for the cleanest mapping — anything larger just gets 
# resized down.

# For an animated sequence, pass multiple image paths (e.g. frame_01.png, 
# frame_02.png...) and they'll all land in the FRAMES list, cycled through by 
# ROTATIONS_PER_FRAME in the main loop.
