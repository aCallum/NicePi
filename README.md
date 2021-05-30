# NicePi

NicePi is a Python based monitoring tool for NiceHash, aimed to be run on a Raspberry Pi with GPIO displays.

![alt text](https://github.com/aCallum/NicePi/blob/main/nciepi.jpg)

## Support Me

Thanks for checking out SafePi. It would be great to have your support in any way possible. Crypto donations, or a coffee to keep me coding are always welcome!

BTC Donations Welcome: 3Fy8MVbx35zMrBnTP6rJt1Cb7fwS4NacvA

Or buy me a coffee: https://ko-fi.com/aCallum

Prerequisites:
1. Almost any RaspberryPi (with GPIO support):
    - https://thepihut.com/collections/raspberry-pi/products/raspberry-pi-zero-wh-with-pre-soldered-header
3. Any SPI/I2C GPIO display:
    - https://thepihut.com/collections/raspberry-pi-screens/products/128x32-2-23inch-oled-display-hat-for-raspberry-pi
4. SD Card 8GB or higher -- image it with Raspberry Pi OS Lite
5. Power Cable & Charger/Battery Bank

Build the Device:
1. Burn the OS in SD Card & 
2. Connect the display to Pi GPIO Pins
3. Plug in Power
4. Install OS
5. Enable SPI in Raspi Config
    - sudo raspi-config
    - select Interface Options > SPI > Yes
6. Reboot the Pi
    - sudo reboot now

Software & Install:
1. Get Nicehash apiKey, apiSecret & orgId - https://www.nicehash.com/my/settings/keys
2. Install Python3, Git, and SPI
    - sudo apt-get update
    - sudo apt-get install python3-pip
    - sudo apt-get install python3-pil
    - sudo apt-get install python3-numpy
    - sudo pip3 install RPi.GPIO
    - sudo pip3 install spidev
    - sudo apt-get install git
4. clone this project to RaspberryPi
    - git clone https://github.com/aCallum/NicePi
5. Edit config.py in nano or other text editor and add your keys from nicehash API
    - nano NicePi/config.py
    - or open with text editor

Run
1. Change to project folder
    - cd NicePi
3. Run it with Python3 
    - sudo python3 main.py

## Support Me

Thanks for checking out SafePi. It would be great to have your support in any way possible. Crypto donations, or a coffee to keep me coding are always welcome!

BTC Donations Welcome: 3Fy8MVbx35zMrBnTP6rJt1Cb7fwS4NacvA

Or buy me a coffee: https://ko-fi.com/aCallum
