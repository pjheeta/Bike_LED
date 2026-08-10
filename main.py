# *** LOADS ALL THE LIBRARIES NEEDED ***
# Network and Socket are for WiFi. 
# APA102 and HallSync are your custom files on the XIAO.
# frames.py contains all animation frame data.

import time
import network
import socket
from machine import Pin
from apa102 import APA102
from hall_sync import HallSync
from frames import make_test_frame


# *** HARDWARE INITIALIZATION ***
# Front Wheel Architecture — 4 arms, 2 faces per arm, 8 strips total
# Each strip has 27 LEDs at 144 LED/meter = 187mm (~7.4") per arm
# Total: 27 LEDs x 8 strips = 216 LEDs
#
# Daisy chain order:
# ESP Box → A1(1-27) → B1(28-54) → A2(55-81) → B2(82-108)
#         → A3(109-135) → B3(136-162) → A4(163-189) → B4(190-216)
#
# A = Front face (hub → rim)
# B = Back face (rim → hub) — columns reversed in frames.py
#
# For 30 LED/meter rear wheel:
# 10" Spokes has 14 LEDs (7/side)

# ****** LED CHANGE HERE — THIS IS THE ONLY LINE YOU NEED TO CHANGE WHEN SWAPPING STRIPS ******
NUM_LEDS = 216  # 27 LEDs x 8 strips (4 arms x 2 faces) — change this ONE value only

NUM_COLUMNS = 60  # How many angular slices per rotation — do not change

strip = APA102(num_leds=NUM_LEDS, brightness=8)  # brightness=8 — plenty bright on dark playa, saves battery
hall = HallSync(pin_num=4)  # Hall sensor on GPIO4 (D3 on XIAO)


# *** AP CONFIGURATION / START WI-FI HOTSPOT ***
# AP_IF means it is in Access Point mode — the XIAO IS the hotspot, other devices connect TO it
# STA_IF would mean the XIAO connects TO an existing WiFi network (not used here)
# ap.active(True) activates the access point. True = on, False = off.
# ap.config sets the essid, the password and the authentication mode. 3 means WPA2.
# By default the XIAO's IP address is 192.168.4.1
# To change the IP address, use ap.ifconfig():
# e.g: ap.ifconfig(('192.168.1.1', '255.255.255.0', '192.168.1.1', '8.8.8.8'))

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='BikeWheel', password='burningman', authmode=3)
print('WiFi started:', ap.ifconfig()[0])


# *** WEB SERVER SETUP ***
# Opens a simple HTTP server on port 80.
# When a request comes in, handle_web() checks for /on or /off and responds.

server = socket.socket()  # Creates a network socket — like picking up a phone before dialing

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# SO_REUSEADDR — crash recovery safety net.
# If the XIAO reboots, port 80 might still be marked "in use" by the old session.
# This line says: if the port is still reserved, grab it anyway.

server.bind(('0.0.0.0', 80))
# 0.0.0.0 means "listen on all available interfaces" — accept connections from anyone on the network.
# Port 80 is the standard HTTP port — why the app connects with just http://192.168.4.1 (no port number needed).

server.listen(1)  # Start listening. 1 = only keep 1 connection waiting in queue at a time.

server.setblocking(False)
# Non-blocking mode — server.accept() checks instantly instead of freezing to wait.
# If no connection is waiting it throws an exception — caught by try/except in handle_web().
# Critical for POV — we can't freeze the timing loop waiting for web requests.


# *** STATE VARIABLES ***
leds_on = True           # Master on/off switch controlled by web server
current_frame = 0        # Which animation frame is currently showing
rot_at_last_frame = 0    # Rotation count when we last advanced the frame
ROTATIONS_PER_FRAME = 5  # How many wheel rotations before advancing to next frame


# *** BUILD FRAMES ***
# Passes NUM_COLUMNS and NUM_LEDS to frames.py — single source of truth stays in main.py.
# frames.py handles front/back face reversal automatically.
# Add more frames here as you build them (circle, square, cross etc.)
FRAMES = [make_test_frame(NUM_COLUMNS, NUM_LEDS)]


# *** WEB REQUEST HANDLER ***
# Called every 100ms from the main loop.
# Checks for incoming HTTP requests and handles /on and /off commands.
# Uses NUM_LEDS so flash colors are always correct regardless of strip size.
def handle_web():
    global leds_on
    try:
        conn, addr = server.accept()
        req = conn.recv(1024).decode()
        if '/on' in req:
            leds_on = True
            strip.show([(0, 255, 0)] * NUM_LEDS)  # Flash green — NUM_LEDS updates automatically
            time.sleep_ms(300)
            print('LEDs ON')
        elif '/off' in req:
            leds_on = False
            strip.show([(255, 0, 0)] * NUM_LEDS)  # Flash red — NUM_LEDS updates automatically
            time.sleep_ms(300)
            strip.off()
            print('LEDs OFF')
        conn.send(b'HTTP/1.1 200 OK\r\n\r\nOK')
        conn.close()
    except:
        pass  # No connection waiting — non-blocking mode throws exception, we ignore it and move on


print('Starting main loop...')
last_web_check = time.ticks_ms()


# *** MAIN LOOP ***
# Runs forever. Every iteration:
# 1. Checks for web requests every 100ms
# 2. Checks safety conditions
# 3. Runs POV timing engine if wheel is spinning
while True:

    # *** CHECK WEB REQUESTS ***
    # Every 100ms regardless of wheel state — keeps WiFi responsive during POV loop.
    now = time.ticks_ms()
    if time.ticks_diff(now, last_web_check) > 100:
        handle_web()
        last_web_check = now

    # *** SAFETY CHECKS ***
    # If LEDs are turned off OR wheel isn't spinning — kill LEDs and skip POV loop.
    # is_spinning() returns False if no hall trigger in the last 1 second.
    # Automatic safety feature — stop pedaling and LEDs go dark.
    if not leds_on or not hall.is_spinning():
        strip.off()
        time.sleep_ms(20)
        continue  # Skip rest of loop, go back to top

    # *** POV TIMING ENGINE ***
    # Gets rotation period from hall sensor.
    # period = how long one full rotation takes in microseconds.
    # e.g. 1,000,000µs = 1 second = 60 RPM (playa speed ~5mph)
    period = hall.get_period()
    if period == 0:
        time.sleep_ms(10)
        continue  # Hall sensor not triggered yet — skip

    # *** FRAME ADVANCEMENT ***
    # Every ROTATIONS_PER_FRAME rotations, advance to next animation frame.
    # % len(FRAMES) wraps back to frame 0 after the last frame — like a GIF looping.
    if hall.rotation_count - rot_at_last_frame >= ROTATIONS_PER_FRAME:
        current_frame = (current_frame + 1) % len(FRAMES)
        rot_at_last_frame = hall.rotation_count

    # column_dur = microseconds each column gets to display
    # e.g. 1,000,000µs ÷ 60 columns = ~16,666µs per column at 60 RPM
    column_dur = period // NUM_COLUMNS
    frame = FRAMES[current_frame]

    # *** POV COLUMN DISPLAY LOOP — THE HEART OF POV ***
    # For each of the 60 columns:
    # 1. Record start time in microseconds
    # 2. Push column colors to LEDs via SPI
    # 3. Calculate how long the SPI write took
    # 4. Sleep the remaining time so each column gets exactly column_dur microseconds
    #
    # Your eye retains each flash briefly — 60 columns at precise intervals
    # creates the illusion of a complete floating image. That's persistence of vision.
    for col in range(NUM_COLUMNS):
        t0 = time.ticks_us()
        strip.show(frame[col])
        elapsed = time.ticks_diff(time.ticks_us(), t0)
        remaining = column_dur - elapsed
        if remaining > 0:
            time.sleep_us(remaining)
