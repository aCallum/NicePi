# NicePi

NicePi is a Python based monitoring tool for NiceHash, aimed to be run on a Raspberry Pi with GPIO displays.

![alt text](https://github.com/aCallum/NicePi/blob/main/nciepi.jpg)

Prerequisites :
1. Almost any RaspberryPi (with GPIO support)
2. Any SPI/I2C GPIO display
3. SD Card 8GB or higher -- image it with Raspberry Pi OS Lite
4. Power Cable & Charger/Battery Bank

Build the Device :
1. Burn the OS in SD Card & 
2. Place the LCD dislay on GPIO Pins
3. Plug in Power
4. Allow to install/Expand OS.
5. Enable SPI in Raspi Config
    sudo raspi-config
    select Interface Options > SPI > Yes
6. Reboot the Pi

Software & Install:
1. Get Nicehash BTCAddress, apiKey, apiSecret & orgId - https://www.nicehash.com/my/settings/keys
2. Install Python3 anf Git
3. clone this project to RaspberryPi (git clone https://github.com/aCallum/NicePi)

Run
1. Change to project folder (cd NicePi)
2. Run it with Python3 (sudo python3 main.py)
