import time
import network
import socket
from machine import Pin
from apa102 import APA102
from hall_sync import HallSync

strip = APA102(num_leds=144, brightness=31)
#strip = APA102(num_leds=78, brightness=31)
hall = HallSync(pin_num=4)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='BikeWheel', password='burningman', authmode=3)
print('WiFi started:', ap.ifconfig()[0])

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 80))
server.listen(1)
server.setblocking(False)

leds_on = True
current_frame = 0
rot_at_last_frame = 0
ROTATIONS_PER_FRAME = 5
NUM_COLUMNS = 60
NUM_LEDS = 78

def make_test_frame():
    frame = []
    for col in range(NUM_COLUMNS):
        color = (255, 0, 0) if col % 2 == 0 else (0, 0, 255)
        frame.append([color] * NUM_LEDS)
    return frame

FRAMES = [make_test_frame()]

def handle_web():
    global leds_on
    try:
        conn, addr = server.accept()
        req = conn.recv(1024).decode()
        if '/on' in req:
            leds_on = True
            strip.show([(0, 255, 0)] * 78)  # flash green
            time.sleep_ms(300)
            print('LEDs ON')
        elif '/off' in req:
            leds_on = False
            strip.show([(255, 0, 0)] * 78)  # flash red
            time.sleep_ms(300)
            strip.off()
            print('LEDs OFF')
        conn.send(b'HTTP/1.1 200 OK\r\n\r\nOK')
        conn.close()
    except:
        pass

print('Starting main loop...')
last_web_check = time.ticks_ms()

while True:
    # check web every 100ms regardless of wheel state
    now = time.ticks_ms()
    if time.ticks_diff(now, last_web_check) > 100:
        handle_web()
        last_web_check = now

    if not leds_on or not hall.is_spinning():
        strip.off()
        time.sleep_ms(20)
        continue

    period = hall.get_period()
    if period == 0:
        time.sleep_ms(10)
        continue

    if hall.rotation_count - rot_at_last_frame >= ROTATIONS_PER_FRAME:
        current_frame = (current_frame + 1) % len(FRAMES)
        rot_at_last_frame = hall.rotation_count

    column_dur = period // NUM_COLUMNS
    frame = FRAMES[current_frame]

    for col in range(NUM_COLUMNS):
        t0 = time.ticks_us()
        strip.show(frame[col])
        elapsed = time.ticks_diff(time.ticks_us(), t0)
        remaining = column_dur - elapsed
        if remaining > 0:
            time.sleep_us(remaining)