# BikeWheel Project — Command Reference
## Pawan Heeta | Burning Man 2026

---

## 1. LINUX SETUP (Ubuntu/Mint)

### Add user to dialout group (fixes USB permission errors)
```bash
sudo usermod -a -G dialout $USER
# Then reboot
```

### Add esptool to PATH
```bash
echo 'export PATH=$PATH:~/Library/Python/3.9/bin' >> ~/.zshrc
source ~/.zshrc
```

### Install esptool
```bash
pip3 install esptool --break-system-packages
esptool.py version  # confirm 4.12.0+
```

---

## 2. FLASHING MICROPYTHON FIRMWARE

### Download firmware
- URL: https://micropython.org/download/SEEED_XIAO_ESP32S3/
- Get latest preview .bin file

### Put XIAO in bootloader mode
1. Hold BOOT button
2. Press and release RESET
3. Release BOOT

### Flash firmware
```bash
# Erase first
esptool.py --port /dev/ttyACM0 erase_flash

# Flash MicroPython
esptool.py --port /dev/ttyACM0 write_flash 0 SEEED_XIAO_ESP32S3-XXXXXXXX.bin
```

### Find port on Linux
```bash
ls /dev/tty*
# Look for /dev/ttyACM0 or /dev/ttyUSB0
```

---

## 3. THONNY SETUP

- Interpreter: MicroPython (ESP32)
- Port: /dev/ttyACM0 (or /dev/ttyUSB0)
- Tools → Options → Interpreter → Port dropdown

---

## 4. WEBREPL SETUP (Wireless file upload)

### Enable WebREPL on XIAO (run once in Thonny shell)
```python
import webrepl_setup
# Press E to enable
# Set password: bikewheel
```

### Update boot.py to auto-start WebREPL with password
```python
f = open('boot.py', 'w')
f.write("import webrepl\nwebrepl.start(password='bikewheel')\n")
f.close()
```

### Download WebREPL CLI tool
```bash
wget https://raw.githubusercontent.com/micropython/webrepl/master/webrepl_cli.py
```

### Upload a single file wirelessly
```bash
# Connect laptop to BikeWheel WiFi first (password: burningman)
python3 ~/Downloads/webrepl_cli.py -p bikewheel ~/Bike_LED/Front_ESP/main.py 192.168.4.1:/main.py
```

### Download WebREPL GUI (offline browser client)
```bash
wget https://raw.githubusercontent.com/micropython/webrepl/master/webrepl.html
xdg-open webrepl.html
# Connect to ws://192.168.4.1:8266
```

---

## 5. UPLOAD SCRIPTS

### Front ESP upload script (frontUL.sh)
```bash
#!/bin/bash
IP=192.168.4.1
PASS=bikewheel
DIR=~/Bike_LED/Front_ESP

for f in main.py apa102.py hall_sync.py frames.py espnow_tx.py index.html; do
    python3 ~/Downloads/webrepl_cli.py -p $PASS $DIR/$f $IP:/$f
    echo "Uploaded $f"
done
```

### Back ESP upload script (backUL.sh)
```bash
#!/bin/bash
IP=192.168.4.1
PASS=bikewheel
DIR=~/Bike_LED/Back_ESP

for f in main.py apa102.py espnow_rx.py; do
    python3 ~/Downloads/webrepl_cli.py -p $PASS $DIR/$f $IP:/$f
    echo "Uploaded $f"
done
```

### Make scripts executable
```bash
chmod +x ~/Bike_LED/Front_ESP/frontUL.sh
chmod +x ~/Bike_LED/Back_ESP/backUL.sh
```

### Run upload scripts
```bash
# Connect to BikeWheel WiFi first
./frontUL.sh

# Connect to BikeWheelRear WiFi first
./backUL.sh
```

---

## 6. USEFUL MICROPYTHON SHELL COMMANDS (in Thonny)

### List files on device
```python
import os
os.listdir()
```

### Check boot.py contents
```python
f = open('boot.py', 'r')
print(f.read())
f.close()
```

### Quick LED test (27 LEDs red)
```python
from machine import SPI, Pin
spi = SPI(1, baudrate=8_000_000, polarity=0, phase=0, sck=Pin(7), mosi=Pin(9))
data = bytearray(4)
for i in range(27):
    data += bytes([0xE8, 0, 0, 255])
data += bytes([0xFF] * 3)
spi.write(data)
```

### Quick hall sensor test
```python
from machine import Pin
import time
hall = Pin(4, Pin.IN, Pin.PULL_UP)
while True:
    print(hall.value())
    time.sleep_ms(100)
```

### Start WebREPL manually
```python
import webrepl
webrepl.start(password='bikewheel')
```

### Check MT3608 voltage (use multimeter on VOUT+ and GND)
# Target: 5.07V

---

## 7. WIFI NETWORKS

| Network        | Password   | XIAO  | IP           | Use                    |
|----------------|------------|-------|--------------|------------------------|
| BikeWheel      | burningman | Front | 192.168.4.1  | Control + WebREPL      |
| BikeWheelRear  | burningman | Rear  | 192.168.4.1  | WebREPL only           |

---

## 8. WEB CONTROL ENDPOINTS (Front XIAO)

| Endpoint          | Action                    |
|-------------------|---------------------------|
| /                 | PWA control page          |
| /on               | LEDs on                   |
| /off              | LEDs off                  |
| /next             | Next animation pattern    |
| /brightness/N     | Set brightness (1-31)     |
| /ping             | Health check              |
| /status           | JSON status + RPM         |

---

## 9. FILE STRUCTURE

```
~/Bike_LED/
├── Front_ESP/
│   ├── main.py          # POV engine + WiFi + ESP-NOW
│   ├── apa102.py        # SK9822 LED driver
│   ├── hall_sync.py     # A3144 hall sensor driver
│   ├── frames.py        # POV animation frames
│   ├── espnow_tx.py     # Broadcasts RPM to rear XIAO
│   ├── index.html       # PWA control page
│   └── frontUL.sh       # Wireless upload script
├── Back_ESP/
│   ├── main.py          # Ambient glow + ESP-NOW receiver
│   ├── apa102.py        # SK9822 LED driver
│   ├── espnow_rx.py     # Receives RPM from front XIAO
│   └── backUL.sh        # Wireless upload script
├── Android/
│   └── BikeWheelApp.zip # Android APK source
├── Sample_Code/         # Test scripts
├── Guides/              # PDFs and docs
├── Hardware/            # STL and datasheets
└── Firmware/            # MicroPython .bin files
```

---

## 10. HARDWARE PINOUT (Front XIAO ESP32-S3)

| Pin | Label      | Connected to          |
|-----|------------|-----------------------|
| 1   | 5V         | MT3608 VOUT+ + LEDs   |
| 2   | GND        | Common ground         |
| 3   | 3V3        | Hall sensor VCC       |
| 4   | D10/GPIO9  | LED DATA (MOSI)       |
| 6   | D8/GPIO7   | LED CLK (SCK)         |
| 11  | D3/GPIO4   | Hall sensor OUT       |

---

## 11. LED CONFIGURATION

| Wheel | Strips | LEDs/strip | Total LEDs | Strip type    |
|-------|--------|------------|------------|---------------|
| Front | 8      | 27         | 216        | SK9822 144/m  |
| Rear  | 4      | ~10        | 40         | SK9822 30/m   |

Daisy chain order (front):
XIAO → A1→B1→A2→B2→A3→B3→A4→B4

---

## 12. POWER CIRCUIT (Front Wheel)

```
LiPo1+ → [1N5400 diode] \
                          → [ROCKER SWITCH] → MT3608 IN+ → MT3608 VOUT+(5.07V) → XIAO 5V → LEDs
LiPo2+ → [1N5400 diode] /

LiPo1- ──────────────────────────────────────────────────────────────────────────────→ GND
LiPo2- ──────────────────────────────────────────────────────────────────────────────→ GND
```

⚠️ TP4056 charging circuit is completely separate — never connect to riding circuit
⚠️ Rocker switch on positive wire only, never on ground
