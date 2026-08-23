import espnow
import network
import json
import time

BROADCAST_MAC = b'\xff\xff\xff\xff\xff\xff'

class ESPNowBroadcaster:
    def __init__(self):
        self._sta = network.WLAN(network.STA_IF)
        self._sta.active(True)
        self._en = espnow.ESPNow()
        self._en.active(True)
        self._en.add_peer(BROADCAST_MAC)
        self._last_send_ms = 0
        print("[ESP-NOW TX] Ready, MAC:", ':'.join('{:02x}'.format(b) for b in self._sta.config('mac')))

    def send(self, rpm, period_us, is_spinning):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_send_ms) < 100:
            return
        try:
            msg = json.dumps({
                "rpm": round(rpm, 1),
                "period_us": period_us,
                "is_spinning": is_spinning
            })
            self._en.send(BROADCAST_MAC, msg)
            self._last_send_ms = now
        except Exception as e:
            print("[ESP-NOW TX] Error:", e)

    def stop(self):
        self._en.active(False)
