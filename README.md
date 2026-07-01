# Burning Man LED Generator

Super Cool Burning Man Wheel LEDs like the [Monkey Lights POV](https://www.youtube.com/watch?v=W3Gmv9J05eQ) Wheel display


## Built with

 - Python 
 - VSCode, with the Extension 
 - **MicroPico** 
 - Blood, Sweat, and Tears 
 - https://stackedit.io/ - To edit this readme.md file

## Files
**BOM.txt** - All The parts needed

**main.py** | Main loop

  MicroPython looks for main.py, and runs it after boot.py

**apa102.py** | The SPI / LED Driver 

  SK9822 and APA102 use a simple SPI protocol: a start frame, then 4 bytes per LED (brightness + B + G + R), then an end frame. 

**hall_sync.py**  | The Hall Sensor Interrupt

**frames.py** | Frame Data
The Image for the wheel

