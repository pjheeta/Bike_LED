# *** LOADS ALL THE LIBRARIES NEEDED ***
# Network and Socket are for WiFi. 
# APA102 and HallSync are your custom files on the XIAO.

import time
import network
import socket
from machine import Pin
from apa102 import APA102
from hall_sync import HallSync


# *** HARDWARE INITIALIZATION ***
# For 144 LEDs/meter
# Front Wheel has 72 LEDS (36 on each side)
# Back Wheel / Test Wheel has 14 LEDs (7 on each side)
# For 30 LEDs/meter
# 10" Spokes has 14 LEDs (7/side)

# ****** LED CHANGE HERE (1/2) ****** 
strip = APA102(num_leds=14, brightness=31)
hall = HallSync(pin_num=4)

# *** AP Configuration / Start Wi-Fi Hotspot ***
# AP_IF means it is in AP mode, STA_IF means it is in STA mode
# ap.active(True) activates the access point.   True = on, False = off.
# ap.config sets the essid, the password and the authentication mode 3 means WPA2
# by default the XIAO's IP address is 192.168.4.1
# to change the IP address, you can use ap.ifconfig() to set a new IP address, netmask, gateway and DNS server
# e.g:  ap.ifconfig(('192.168.1.1', '255.255.255.0', '192.168.1.1', '8.8.8.8'))

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='BikeWheel', password='burningman', authmode=3)

print('WiFi started:', ap.ifconfig()[0])

# *** WEB SERVER SETUP ***
# Open a socket on port 80 and listen for incoming connections.  When a connection is received, 
# check the request for /on or /off and set the leds_on variable accordingly.  Then send a simple 
# HTTP response back to the client.

server = socket.socket()  # Creates a network socket
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Sets a socket option to allow the socket to be reused
# If the XIAO crashes or reboots, the port 80 might still be marked as "in use" by the old session. 
# Without this line, the new server would fail to start with "address already in use" error. 
# This line says — if the port is still technically reserved, grab it anyway. 
# Basically a crash recovery safety net.

server.bind(('0.0.0.0', 80))  # Tells the socket which IP and port to listen on: 0.0.0 means "all available interfaces" 
# and 80 is the standard HTTP port.  This is why the app connects with just http://192.168.4.1 and doesn't need a port number.
# Browsers and HTTP clients assume port 80 by default

server.listen(1) # Starts listening for incoming connections. The 1 means only keep 1 connection waiting in the queue at a time
server.setblocking(False) # setblocking(False) makes the socket non-blocking, so that the main loop can continue to run even if  
# there are no incoming connections.  This is important because we want to be able to update the LEDs even if there is no web traffic.


# *** DECLARING THE STATE VARIABLES FOR THE MAIN LOOP ***
leds_on = True  # Master on/off switch for the LEDs
current_frame = 0 # Which animation frame is currently being displayed
rot_at_last_frame = 0 # tracks when to advance to the next frame based on rotations
ROTATIONS_PER_FRAME = 5 # How many rotations to wait before advancing to the next frame
NUM_COLUMNS = 60 # How many columns of pixels to display per frame
# ****** LED CHANGE HERE (2/2) ****** 
NUM_LEDS = 14 # How many LEDs per arm — all other LED counts in the code use this variable automatically


# *** TEST FRAME GENERATOR ***
# Creates a simple test pattern — alternating red and blue vertical columns.
def make_test_frame():
    frame = []
    for col in range(NUM_COLUMNS):
        color = (255, 0, 0) if col % 2 == 0 else (0, 0, 255)
        frame.append([color] * NUM_LEDS)
    return frame

FRAMES = [make_test_frame()]  # A list containing all the frames to be displayed.  
# Right now it only has one frame, but you can add more frames to the list to create an animation.


# *** WEB REQUEST HANDLER ***
# Checks if anyone sent an HTTP request. If URL contains /on — turn LEDs on (flash green). If /off — turn off. 
# The try/except means if no request came in, it just moves on silently.
# NUM_LEDS is used here so this never needs to change when swapping strips.
def handle_web():
    global leds_on
    try:
        conn, addr = server.accept()
        req = conn.recv(1024).decode()
        if '/on' in req:
            leds_on = True
            strip.show([(0, 255, 0)] * NUM_LEDS)  # flash green — uses NUM_LEDS automatically
            time.sleep_ms(300)
            print('LEDs ON')
        elif '/off' in req:
            leds_on = False
            strip.show([(255, 0, 0)] * NUM_LEDS)  # flash red — uses NUM_LEDS automatically
            time.sleep_ms(300)
            strip.off()
            print('LEDs OFF')
        conn.send(b'HTTP/1.1 200 OK\r\n\r\nOK')
        conn.close()
    except:
        pass

print('Starting main loop...')
last_web_check = time.ticks_ms()

# *** MAIN LOOP ***
# The main loop checks for web requests every 100ms, and if the LEDs are on and the wheel is spinning, it calculates 
# how long to display each column of the current frame based on the wheel's rotation period. It then updates the LEDs accordingly.
while True:
    # check web every 100ms regardless of wheel state
    now = time.ticks_ms()
    if time.ticks_diff(now, last_web_check) > 100:
        handle_web()
        last_web_check = now

    # *** SAFETY CHECKS ***
    # If LEDs are turned off OR the wheel isn't spinning — kill the LEDs and skip the POV loop. 
    # This is the safety light fallback — when you're not riding, LEDs go off automatically.
    if not leds_on or not hall.is_spinning():
        strip.off()
        time.sleep_ms(20)
        continue

    # *** POV (Persistence of Vision) TIMING ENGINE ***
    # The hall sensor measures how long it takes for the wheel to make one full rotation.  
    # This is used to calculate how long to display each column of the current frame.

    period = hall.get_period()   # period is how long one full rotation takes in microseconds (e.g. 500,000µs = 0.5 seconds). 
    # Divide by 60 columns = each column gets ~8,333µs to display
    if period == 0:
        time.sleep_ms(10)
        continue

    # *** FRAME ADVANCEMENT ***
    # Every 5 rotations, advance to the next animation frame. 
    # Right now there's only one frame so it just loops back to itself.
    if hall.rotation_count - rot_at_last_frame >= ROTATIONS_PER_FRAME:
        current_frame = (current_frame + 1) % len(FRAMES)
        rot_at_last_frame = hall.rotation_count

    column_dur = period // NUM_COLUMNS
    frame = FRAMES[current_frame]

    # *** POV COLUMN DISPLAY LOOP ***
    # This is the heart of POV. For each of the 60 columns:
    # 1. Record the start time
    # 2. Push that column's colors to the LEDs instantly via SPI
    # 3. Calculate how long that took
    # 4. Sleep the remaining time so each column gets exactly the right display duration
    # Because your eye retains each flash briefly, 60 columns displayed at precise intervals creates the illusion of a floating image.
    for col in range(NUM_COLUMNS):
        t0 = time.ticks_us()
        strip.show(frame[col])
        elapsed = time.ticks_diff(time.ticks_us(), t0)
        remaining = column_dur - elapsed
        if remaining > 0:
            time.sleep_us(remaining)