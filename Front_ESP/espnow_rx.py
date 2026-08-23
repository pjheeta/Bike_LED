import espnow
import network
import json
import time

TIMEOUT_MS = 2000  # Fall back to ambient if no signal for 2 seconds

class ESPNowReceiver:
    def __init__(self):
        self._sta = network.WLAN(network.STA_IF)
        self._sta.active(True)
        self._en = espnow.ESPNow()
        self._en.active(True)
        self._latest = {"rpm": 0.0, "period_us": 0, "is_spinning": False}
        self._last_rx_ms = 0
        print("[ESP-NOW RX] Listening for front wheel...")

    def poll(self):
        try:
            host, msg = self._en.recv(0)
            if msg is not None:
                self._latest = json.loads(msg)
                self._last_rx_ms = time.ticks_ms()
        except:
            pass

    def get_latest(self):
        now = time.ticks_ms()
        if self._last_rx_ms == 0 or time.ticks_diff(now, self._last_rx_ms) > TIMEOUT_MS:
            return {"rpm": 0.0, "period_us": 0, "is_spinning": False}
        return self._latest

    def is_connected(self):
        return time.ticks_diff(time.ticks_ms(), self._last_rx_ms) < TIMEOUT_MS

    def stop(self):
        self._en.active(False)
