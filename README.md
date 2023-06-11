# Stage2-IndEnt-Major-Piano-Teacher
This is the source code for my SACE Stage 2 Industry and Entrepreneurial Solutions Major project. I used a Raspberry PI, 5 Inch DSI touch screen and WS2812B LED Strip

## Parts Used (from core electronics)
 - [1M LED Strip - WS2812B](https://core-electronics.com.au/1m-rgb-led-strip-ws2812b-144-per-meter-white-strip-weatherproof.html)
 - [5” DSI Touch Display (800×480)](https://core-electronics.com.au/5inch-capacitive-ips-touch-display-for-raspberry-pi-800480-dsi-interface-low-power.html )
 - [Raspberry Pi 3 Model B+](https://core-electronics.com.au/raspberry-pi-3-model-b-plus.html )
 
## Libraries
GUI: [PyQt5](https://pypi.org/project/PyQt5/#files) - sudo pip3 install pyqt5
LED Operation: [rpi_ws281x](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel) - sudo pip3 rpi_ws281x adafruit-circuitpython-neopixel
MIDI file reading: [pretty_midi](https://pypi.org/project/pretty_midi/#files) - sudo pip3 install pretty_midi
 
## Instructions
 1) Clone this repository to your raspberry PI
 2) Download and install the libraries above
 3) Connect a WS2812B LED strip to GPIO 18
 5) In the refresh_songs() function, change the os.walk directory to the location that your USBs are mounted to
 6) run the program with python3 using Sudo privellages - Sudo python3 gui.py

## To get PI to work with WS2812B LEDs
 1) install the library to operate the LED - sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
 2) force reinstall blinka - sudo python3 -m pip install --force-reinstall adafruit-blinka
 3) perform an apt-get update - sudo apt-get update
 4) Install python-dev git and scons - sudo apt-get install gcc make build-essential python-dev git scons swig
 5) open the snd-blacklist file - sudo nano /etc/modprobe.d/snd-blacklist.conf
 6) type inside of the file "blacklist snd_bcm2835" and save it
 7) open the config file - sudo nano /boot/config.txt
 8) comment (using #) the line with "dtparam=audio=on"
 9) rebot - sudo reboot
