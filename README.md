
# Burning Man LED Generator

  

Super Cool Burning Man Wheel LEDs like the [Monkey Lights POV](https://www.youtube.com/watch?v=W3Gmv9J05eQ) Wheel display

Burning Man LEDs based on Monkey Light Design

🚲 Updated POV BOM — Qlife Racer (26" Wheel)

⚠️ Key Decision First: Use the FRONT wheel

The rear wheel has a hub motor — spoke geometry is different, it's heavier, and mounting is messier. Front wheel is clean, symmetrical, and easy to work with. All recommendations below assume front wheel.

Two things worth flagging for Burning Man specifically:

1. Balance matters at speed — once you mount the LED arm + battery, the wheel will be slightly unbalanced. At playa speeds (~15mph) this is usually fine, but mount the battery as close to center hub as possible to minimize it.

2. Don't tap the e-bike battery — even though the bike has 36V on board, keeping the LED system on its own LiPo keeps it modular, safe, and swappable without touching the motor system.


## Built with

  

- Python

- VSCode, with the Extension

-  **MicroPico**

- Blood, Sweat, and Tears

- https://stackedit.io/ - To edit this readme.md file

  

## Files

**BOM.txt** - All The parts needed

  

**main.py** | Main loop

  

MicroPython looks for main.py, and runs it after boot.py

  

**apa102.py** | The SPI / LED Driver

  

SK9822 and APA102 use a simple SPI protocol: a start frame, then 4 bytes per LED (brightness + B + G + R), then an end frame.

  

**hall_sync.py** | The Hall Sensor Interrupt

  

**frames.py** | Frame Data

  

The Image for the wheel

  

**convertImage.py** | Image converter

  

Converts an image into frame data and adds it to frame.py