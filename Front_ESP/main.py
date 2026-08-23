"""
main.py — Front Wheel XIAO
============================
- 216 LEDs (8 strips x 27 LEDs)
- POV timing engine driven by hall sensor
- WiFi AP (BikeWheel / burningman)
- Serves PWA control page at http://192.168.4.1
- ESP-NOW broadcasts RPM to rear XIAO

Endpoints:
  GET /          → serves index.html (PWA)
  GET /on        → LEDs on
  GET /off       → LEDs off
  GET /next      → next animation frame
  GET /brightness/N → set brightness 1-31
  GET /ping      → health check
  GET /status    → JSON {leds_on, rpm, is_spinning}

Upload to front XIAO:
  main.py, apa102.py, hall_sync.py, frames.py, espnow_tx.py, index.html
"""

import time
import network
import socket
import json
from apa102 import APA102
from hall_sync import HallSync
from frames import make_rainbow_frame, make_cross_frame
from espnow_tx import ESPNowBroadcaster

# ── Config ────────────────────────────────────────────────────────────────────
NUM_LEDS    = 216
NUM_COLUMNS = 60
BRIGHTNESS  = 8

# ── Hardware ──────────────────────────────────────────────────────────────────
strip = APA102(num_leds=NUM_LEDS, brightness=BRIGHTNESS)
hall  = HallSync(pin_num=4)

# ── ESP-NOW ───────────────────────────────────────────────────────────────────
broadcaster = ESPNowBroadcaster()

# ── WiFi AP ───────────────────────────────────────────────────────────────────
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='BikeWheel', password='burningman', authmode=3)
print('WiFi AP:', ap.ifconfig()[0])

# ── Web server ────────────────────────────────────────────────────────────────
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 80))
server.listen(1)
server.setblocking(False)

# ── Load PWA HTML ─────────────────────────────────────────────────────────────
try:
    with open('index.html', 'r') as f:
        INDEX_HTML = f.read()
    print('PWA loaded')
except:
    INDEX_HTML = '<h1>BikeWheel</h1><a href="/on">ON</a> <a href="/off">OFF</a>'
    print('index.html not found — using fallback')

# ── State ─────────────────────────────────────────────────────────────────────
leds_on            = True
current_frame_idx  = 0
rot_at_last_frame  = 0
ROTATIONS_PER_FRAME = 5

# ── Build frames ──────────────────────────────────────────────────────────────
FRAMES = [
    make_rainbow_frame(NUM_COLUMNS, NUM_LEDS),
    make_cross_frame(NUM_COLUMNS, NUM_LEDS),
]

# ── Web handler ───────────────────────────────────────────────────────────────
def handle_web():
    global leds_on, current_frame_idx, BRIGHTNESS

    try:
        conn, addr = server.accept()
        req = conn.recv(2048).decode()
        path = req.split(' ')[1] if ' ' in req else '/'

        # ── Serve PWA ──────────────────────────────────────────────────
        if path == '/' or path == '/index.html':
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
            conn.send(INDEX_HTML.encode())

        # ── LED on ─────────────────────────────────────────────────────
        elif path == '/on':
            leds_on = True
            strip.show([(0, 255, 0)] * NUM_LEDS)
            time.sleep_ms(200)
            print('ON')
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"ok":true}')

        # ── LED off ────────────────────────────────────────────────────
        elif path == '/off':
            leds_on = False
            strip.off()
            print('OFF')
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"ok":true}')

        # ── Next pattern ───────────────────────────────────────────────
        elif path == '/next':
            current_frame_idx = (current_frame_idx + 1) % len(FRAMES)
            print('Frame:', current_frame_idx)
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"ok":true}')

        # ── Brightness /brightness/N ───────────────────────────────────
        elif path.startswith('/brightness/'):
            try:
                val = int(path.split('/')[-1])
                BRIGHTNESS = max(1, min(31, val))
                strip.brightness = BRIGHTNESS
                print('Brightness:', BRIGHTNESS)
            except:
                pass
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"ok":true}')

        # ── Ping ───────────────────────────────────────────────────────
        elif path == '/ping':
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"pong":true}')

        # ── Status ─────────────────────────────────────────────────────
        elif path == '/status':
            rpm = hall.get_rpm()
            resp = json.dumps({
                "leds_on": leds_on,
                "rpm": round(rpm, 1),
                "is_spinning": hall.is_spinning(),
                "brightness": BRIGHTNESS,
                "frame": current_frame_idx
            })
            conn.send(('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + resp).encode())

        else:
            conn.send(b'HTTP/1.1 404 Not Found\r\n\r\nNot found')

        conn.close()
    except:
        pass

# ── Main loop ─────────────────────────────────────────────────────────────────
print('Front wheel ready —', NUM_LEDS, 'LEDs')
print('Connect to WiFi: BikeWheel / burningman')
print('Open browser: http://192.168.4.1')

last_web_check = time.ticks_ms()

while True:

    now = time.ticks_ms()
    if time.ticks_diff(now, last_web_check) > 100:
        handle_web()
        last_web_check = now

    # Broadcast RPM to rear XIAO
    broadcaster.send(
        rpm=hall.get_rpm(),
        period_us=hall.get_period(),
        is_spinning=hall.is_spinning()
    )

    # Safety — LEDs off when not spinning or switched off
    if not leds_on or not hall.is_spinning():
        strip.off()
        time.sleep_ms(20)
        continue

    period = hall.get_period()
    if period == 0:
        time.sleep_ms(10)
        continue

    # Advance frame every N rotations
    if hall.rotation_count - rot_at_last_frame >= ROTATIONS_PER_FRAME:
        current_frame_idx = (current_frame_idx + 1) % len(FRAMES)
        rot_at_last_frame = hall.rotation_count

    # POV column display
    column_dur = period // NUM_COLUMNS
    frame = FRAMES[current_frame_idx]

    for col in range(NUM_COLUMNS):
        t0 = time.ticks_us()
        strip.show(frame[col])
        elapsed = time.ticks_diff(time.ticks_us(), t0)
        remaining = column_dur - elapsed
        if remaining > 0:
            time.sleep_us(remaining)
