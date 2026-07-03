import network
import socket

# Start access point
ap = network.WLAN(network.AP_IF)
ap.active(False)  # reset it first
ap.active(True)
ap.config(essid='BikeWheel', password='burningman', authmode=3)
print('Secured:', ap.config('authmode'))



# Webserver code
HTML = b"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BikeWheel</title>
<style>
body{background:#0a0a0f;color:#e2e8f0;font-family:sans-serif;
text-align:center;padding:30px;max-width:360px;margin:0 auto}
h1{font-size:20px;margin-bottom:4px}
p{color:#64748b;font-size:13px;margin-bottom:24px}
.row{display:flex;gap:10px;margin-bottom:12px}
button{flex:1;padding:14px;border:none;border-radius:10px;
font-size:16px;font-weight:600;cursor:pointer}
.on{background:#10b981;color:#fff}
.off{background:#ef4444;color:#fff}
.info{background:#1e293b;color:#94a3b8;font-size:12px;
border-radius:8px;padding:12px;margin-top:16px}
</style></head><body>
<h1>BikeWheel</h1>
<p>Connected to XIAO ESP32-S3</p>
<div class="row">
  <form action="/on" method="get">
    <button class="on" type="submit">ON</button></form>
  <form action="/off" method="get">
    <button class="off" type="submit">OFF</button></form>
</div>
<div class="info">192.168.4.1 &nbsp;|&nbsp; BikeWheel v1.0</div>
</body></html>"""

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(5)
print('Server running at http://192.168.4.1')

leds_on = True
while True:
    conn, addr = s.accept()
    req = conn.recv(1024).decode()
    if '/on' in req:
        leds_on = True
        print('LEDs ON')
    elif '/off' in req:
        leds_on = False
        print('LEDs OFF')
    conn.send(HTML)
    conn.close()