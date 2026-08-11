# Burning Man LED Wheel

<p align="center">
  <img src="wheel.svg" width="200" height="200" alt="Spinning LED wheel animation"/>
</p>

<p align="center">
  Super cool Burning Man wheel LEDs inspired by:
</p>
<p align="left">
  - <a href="https://www.youtube.com/watch?v=W3Gmv9J05eQ">Monkey Lights POV</a>
</p>
<p align="left">
  - Luca Schultz's project <a href="https://github.com/BikeBeamer/BikeBeamer">BikeBeamer</a> 
</p>
<p align="left">
  - Adafruit Industries <a href="https://learn.adafruit.com/bike-wheel-pov-display/prep-leds-and-breadboard?view=all">BikeWheel POV Display with Pro Trinket</a> 
</p>

---

## Overview

POV (Persistence of Vision) LED display for a bike wheel. Animated images appear to float in the spinning wheel, visible from both sides. Controlled via WiFi from your phone — no app needed, although an Android app was created.

This project began with the idea of only having one LED strip per side. However, you would need to bike in excess of 20 mph to generate a stable image. Since this project was built for Burning Man, where the max speed is 5 mph on the playa, a single LED strip per arm wouldn't work.

After consulting with Luca Schultz (BikeBeamer builder), the design changed to **4 arms per wheel** with LED strips on both faces of each arm — 8 LED strips per wheel total. At around 5 mph, the image flashes 4 times per rotation, making basic shapes such as squares, circles, and the Man himself clearly visible.

My project uses a Vivi e-bike with 27.5" wheels. The **front wheel** uses LED strips with 144 LEDs/meter for maximum resolution, while the **back wheel** uses LED strips with 30 LEDs/meter for ambient glow patterns. Maybe in Burning Man 2027, both wheels will use the same LED counts.

⚠️ **Both Wheels are different!** The front wheel allows a longer LED strip. Due to e-bike design, the rear wheel has the hub motor — which means the distance from the hub to the rim is shorter. Henceforth, the spoke geometry is different, giving a shorter strip on the back wheel.

This version of Bike LED is for the 2026 Burning Man. A new repository will be created for the 2027 Burning Man project.

---

## Hardware

| Component | Notes |
|-----------|-------|
| 2x XIAO ESP32-S3 | Main controller — WiFi + MicroPython. One per wheel. |
| SK9822 LED strips (144 LEDs/m) | Black PCB, IP30 — Front wheel: 8 strips × 27 LEDs = 216 LEDs total |
| SK9822 LED strips (30 LEDs/m) | Black PCB, IP30 — Rear wheel: 8 strips × 7 LEDs = 56 LEDs total |
| 3x LiPo 3.7V 2000mAh | 2x per front wheel (parallel for more capacity) + 1x rear wheel. All removable nightly for charging via JST connector. |
| 3x TP4056 USB-C | LiPo charger with protection circuit — one per battery |
| 2x MT3608 boost converter | Steps 3.7V LiPo up to 5.07V for LEDs and XIAO. LEDs require 5V to operate correctly. |
| 2x A3144 hall effect sensor | Rotation sync — fires one interrupt per revolution via falling edge trigger |
| 2x 1N5400 Schottky diode | One per positive wire on front wheel parallel battery pair — prevents cross-charging between batteries if voltage mismatch is present |
| 2x 6mm neodymium magnet | Mounts on fork dropout (stationary), triggers hall sensor once per rotation |
| 8x Aluminum flat bar 1/8" × 1/2" | LED arm material. Length depends on spoke measurement — cut after measuring actual bike. 4 per wheel. |
| 2x ABS enclosure 80×50×26mm | Hub-mounted via velcro + zip tie, houses all electronics |
| 2x SPST rocker switch 10×15mm | Kill switch — mounted on long side wall of enclosure |
| Kapton/polyimide tape | Applied between LED strip and aluminum bar to prevent electrical shorts |
| Velcro straps 3/4" | Secures enclosure to hub, secures components inside enclosure |
| Zip ties | Secures LED arms to spokes at hub end and rim end |
| Hot glue | Seals wire exit holes against playa dust |
| MG Chemicals 419D | Conformal coat — applied to all boards after testing is complete |

---

## Four-Arm Design

Both wheels use the same 4-arm layout — arms mounted at 90° intervals around the wheel, giving 4 image flashes per rotation at playa speed.

```
        ARM 1 (0°)
    ● ● ● ● ● ● ●      ← LEDs face right (A face)
    ═══════════════     ← Aluminum bar
    ● ● ● ● ● ● ●      ← LEDs face left  (B face — reversed in firmware)
            │
ARM 4 ══ HUB ══ ARM 2   ← XIAO + battery enclosure velcro'd to hub
            │
        ARM 3 (180°)
```

### Front Wheel — 144 LEDs/m

- **4 arms** at 90° apart
- **2 strips per arm** — A face (front) and B face (back)
- **27 LEDs per strip** at 144/m = 187mm (~7.4") per arm
- **216 LEDs total** across 8 strips
- **Daisy chain order:** XIAO → A1(1-27) → B1(28-54) → A2(55-81) → B2(82-108) → A3(109-135) → B3(136-162) → A4(163-189) → B4(190-216)

**LED table:**

| Strip | Start LED | End LED | Arm | Face |
|-------|-----------|---------|-----|------|
| A1 | 1 | 27 | Arm 1 | Front |
| B1 | 28 | 54 | Arm 1 | Back (reversed) |
| A2 | 55 | 81 | Arm 2 | Front |
| B2 | 82 | 108 | Arm 2 | Back (reversed) |
| A3 | 109 | 135 | Arm 3 | Front |
| B3 | 136 | 162 | Arm 3 | Back (reversed) |
| A4 | 163 | 189 | Arm 4 | Front |
| B4 | 190 | 216 | Arm 4 | Back (reversed) |

⚠️ **Back face strips (B1, B2, B3, B4) must be reversed in firmware.** The B strip runs rim → hub (opposite direction to the A strip), so the image would appear upside down without reversal. This is handled automatically in `frames.py` via `list(reversed(...))`.

**Animations:** Circle, square, cross, rainbow — simple geometric shapes chosen specifically because they are symmetric (look identical from both sides of the wheel) and clearly visible at 5 mph playa speeds.

---

### Rear Wheel — 30 LEDs/m

- **4 arms** at 90° apart
- **2 strips per arm** — A face (front) and B face (back)
- **7 LEDs per strip** at 30/m = ~233mm per arm
- **56 LEDs total** across 8 strips
- **Purpose:** Ambient glow and simple patterns — not detailed POV images
- Rear wheel has hub motor which shortens effective spoke length vs front wheel
- At 30 LEDs/m resolution is too low for detailed images — but rainbow, solid color, and simple shapes look great at any speed

**Powered by:** 1x 2000mAh LiPo — lighter draw than front wheel, single battery is sufficient.

---

## Power Architecture

⚠️ **Two completely separate circuits — never combine them.**

**Riding circuit (wheel spinning):**
```
LiPo → [1N5400 diode] → MT3608 (5.07V) → XIAO + LED strips
```
*(Front wheel: 2x LiPo in parallel via diodes. Rear wheel: single LiPo, no diodes needed.)*

**Charging circuit (parked at camp):**
```
USB-C wall charger → TP4056 → LiPo battery
```
The TP4056 is **never** in the riding circuit. Each LiPo unplugs via JST connector for individual overnight charging.

---

## Burning Man Notes

- **Balance** — mount battery as close to hub center as possible to minimize vibration
- **Don't tap the e-bike battery** — keep LED system on its own LiPo, modular and safe
- **Nightly charging** — LiPo velcro-mounts to enclosure floor, unplugs via JST in seconds
- **Playa-proof** — hot glue all wire exits, apply MG Chemicals 419D conformal coat to all boards after testing
- **Kill switch** — rocker switch on enclosure wall cuts all power instantly
- **Safety mode** — if hall sensor stops triggering, firmware automatically switches to alternating white safety LEDs

---

## Built With

- MicroPython
- Thonny (MicroPython Code IDE)
- VS Code
- MarkEdit and the home extension MarkView
- Cool people such as Luca (BikeBeamer)
- Blood, sweat, and tears
- claude.ai for tips, explanation, lessons, and making me order the wrong parts
- [StackEdit](https://stackedit.io/) for this README

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Main loop — WiFi server + POV timing. Auto-runs on boot |
| `apa102.py` | SPI driver for SK9822/APA102 LED strip |
| `hall_sync.py` | Hall sensor interrupt handler — measures rotation period |
| `frames.py` | Frame data — circle, square, cross, rainbow animations |
| `convertImage.py` | Laptop-side script — converts PNG to `frames.py` format |
| `BOM.txt` | Full bill of materials with sources and prices |

**main.py flow:**
```
Boot → Start WiFi + Web Server
         ↓
Loop → Check web requests every 100ms
         ↓
      Wheel spinning? No → LEDs off (safety)
         ↓ Yes
      Get rotation period from hall sensor
         ↓
      Display 60 columns timed to rotation speed
         ↓
      Repeat forever
```

**apa102.py SPI chain:**
```
XIAO GPIO9 (MOSI) ──→ DI ──→ LED 1 ──→ LED 2 ──→ ... ──→ LED 216
XIAO GPIO7 (SCK)  ──→ CI ──→ LED 1 ──→ LED 2 ──→ ... ──→ LED 216

Every strip.show() call sends:
[00 00 00 00]        ← Start frame — "attention LEDs!"
[FF bb gg rr]        ← LED 1 color (4 bytes — note B,G,R order not R,G,B)
...repeat per LED...
[FF FF FF FF...]     ← End frame — "that's all!"
```

**hall_sync.py flow:**
```
Magnet passes sensor
        ↓
Pin goes HIGH → LOW (falling edge)
        ↓
Hardware interrupt fires instantly
        ↓
_on_trigger() records timestamp + period + count
        ↓
main.py reads period_us → calculates column timing
main.py reads rotation_count → advances animation frame
main.py calls is_spinning() → decides whether to show LEDs
```

---

## WiFi Control

The XIAO acts as its own WiFi access point — no internet or router needed.

1. Connect phone to **BikeWheel** network (password: `burningman`)
2. Open Android app or browser → `192.168.4.1`
3. Control on/off, brightness, speed, safety mode, select animation frame

---

## Animation Frames

Originally planned: Nyan Cat, Angine de Poitrine polka dot mask, Joe's face.

After consulting with Luca (BikeBeamer) and calculating that 5 mph playa speed only gives ~1 rotation/second with a single arm, the design changed to 4 arms and simple geometric shapes that read clearly at low flash rates:

- 🔴🔵 **Test pattern** — alternating red/blue columns (confirms POV timing)
- ⭕ **Circle** — glowing cyan ring floating in the wheel
- 🟧 **Square** — orange square outline
- ✚ **Cross** — pink plus sign
- 🌈 **Rainbow** — full color waterfall, works at any speed

Images will still be added for testing and showing off to people at camp. 😄

---

## Image Conversion Pipeline

Design artwork at **60 × 27 pixels** in any image editor → run `convertImage.py` on laptop → upload `frames.py` to XIAO via Thonny → image appears on spinning wheel.

---

## License

MIT
