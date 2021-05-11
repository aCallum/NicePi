import config

import time
import numpy as np
from datetime import datetime, timedelta
from time import mktime

import nicehash

if config.RUN_EMULATOR:
    import cv2
else:
    import sys
    sys.path.append('./drivers')
    import SPI
    import SSD1305

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def inverse_lerp(a, b, value):
    if a != b:
        return clamp((value - a) / (b - a), 0, 1)
    return 0

def lerp(a, b, t):
    return a + (b-a) * clamp(t, 0, 1)

def get_price():
    data = public_api.get_current_prices()
    return data["BTCUSDC"] * config.USD_GBP

# Create public api object
public_api = nicehash.public_api(False)

# Create public api object
private_api = nicehash.private_api(False)

if config.RUN_EMULATOR:
    imageEncoding = 'RGB'
else:
    imageEncoding = '1'
    # Raspberry Pi pin configuration:
    RST = None     # on the PiOLED this pin isnt used
    # Note the following are only used with SPI:
    DC = 24
    SPI_PORT = 0
    SPI_DEVICE = 0

    # 128x32 display with hardware SPI:
    disp = SSD1305.SSD1305_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
    #disp = SSD1305.SSD1305_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)
    # Initialize library.
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()    

speedData = []

frameSize = (128, 32)
timeCheck = time.time()

font = ImageFont.truetype("fonts/04B_03__.TTF", 8)
font2 = ImageFont.truetype("fonts/Nunito-ExtraLight.ttf", 12)
currencyFont = ImageFont.truetype("fonts/lilliput steps.ttf", 8)
bitcoinfont = ImageFont.truetype("fonts/bitcoin.ttf", 14)

screen_x_offset = frameSize[0]

startTime = time.time()
displayCheck = 0
displayToShow = 0

currentUnpaidBalance = 0
previousUnpaidBalance = 0

currentBalance = 0
previousBalance = 0

currentTotalAceptedSpeed = 0
previousTotalAcceptedSpeed = 0

currentProfitability = 0
previousProfitability = 0
profitabilityGBP = 0

nextAvailablePayout = 0
prevAvailablePayout = 0

est_time_withdrawal = datetime.now()

usdgbp = get_price()

firstRun = True

error = ""

while True:

    screen_x_offset -= 1

    if screen_x_offset <= 0 :
        screen_x_offset = frameSize[0]

    delta = inverse_lerp(0, 15, displayCheck)

    displayCheck = time.time() - startTime

    if (firstRun or (time.time() - timeCheck) > 60):

        timeCheck = time.time()
        firstRun = False

        try:
            data = private_api.get_rigs()
            accountData = private_api.get_accounts_for_currency('BTC')
        except Exception as e:
            displayToShow = -1
            error = e
            continue
        

        try:
            previousProfitability = currentProfitability
            currentProfitability = float(data["totalProfitability"])

            previousUnpaidBalance = currentUnpaidBalance
            currentUnpaidBalance = float(data["unpaidAmount"])

            previousBalance = currentBalance
            currentBalance = float(accountData["available"]) 

            # prevAvailablePayout = data["lastPayoutTimestamp"]
            nextAvailablePayout = data["nextPayoutTimestamp"]

            rigCount = int(data["totalRigs"])
            previousTotalAcceptedSpeed = currentTotalAceptedSpeed

            currentTotalAceptedSpeed = 0
            for i in range(rigCount):
                if data["miningRigs"][i]["minerStatus"] == "MINING":
                    currentTotalAceptedSpeed += float(data["miningRigs"][i]["stats"][0]["speedAccepted"])

        except Exception as e:
            displayToShow = -1
            error = e
            continue

        est_time_withdrawal = (0.0005 - (currentBalance + currentUnpaidBalance)) / (currentProfitability / 24.)
        est_time_withdrawal = timedelta(hours = est_time_withdrawal)
        est_time_withdrawal += datetime.now()
        
        usdgbp = get_price()
        profitabilityGBP = currentProfitability * usdgbp

    if (currentBalance > previousBalance) and (previousBalance > 0):
        image = Image.open('images/bitcoins.bmp').convert(imageEncoding)
        image = image.resize((128, 128), Image.ANTIALIAS)
        image = ImageChops.offset(image, 0, -screen_x_offset * 2)
        image = image.crop((0, 0, 128, 32))
        draw = ImageDraw.Draw(image)

        draw.rectangle([23, 10, frameSize[0] - 23, frameSize[1] - 10], fill="black")
        draw.text((26, 9), "E", fill='white', font=bitcoinfont)
        draw.text((36, 8), "{:.8f}".format(currentBalance - previousBalance), fill="white", font=font2)

    else:

        image = Image.new(imageEncoding, (frameSize))
        draw = ImageDraw.Draw(image)

        if displayCheck > (60/3):
            displayToShow += 1
            displayCheck = 0
            startTime = time.time()
            if displayToShow > 2:
                displayToShow = 0

        if displayToShow == -1:
            draw.text((0, -1), "Error Receiving Data", fill='white', font=font)
            draw.text((0, 32-6), "{0}".format(error), fill='white', font=font)

        if displayToShow == 0:
        
            draw.text((0, -1), "Current Profitability", fill='white', font=font)
            draw.text((0, 6), "E", fill='white', font=bitcoinfont)
            draw.text((9, 5), "{:.8f}".format(currentProfitability), fill='white', font=font2)
            draw.text((75, 12), "/24h", fill='white', font=font)

            draw.text((0, 32-8), "=£", fill='white', font=currencyFont)
            draw.text((12, 32-6), "{:.2f}".format(profitabilityGBP), fill='white', font=font)

            if config.SHOW_INTERPOLATED_VALUE:
                acceptedSpeed_lbl = lerp(previousTotalAcceptedSpeed, currentTotalAceptedSpeed, delta)
            else:
                acceptedSpeed_lbl = currentTotalAceptedSpeed

            draw.text((64, 32-6), "{:.2f} MH/s".format(acceptedSpeed_lbl), fill='white', font=font)
        
        if displayToShow == 1:      
            
            draw.text((0, -1), "Current Balance", fill='white', font=font)            

            # I show the TOTAL BALANCE HERE, so current balance + unpaid mining balance!

            if config.SHOW_INTERPOLATED_VALUE:
                currentBalance_lbl = lerp(previousUnpaidBalance + previousBalance, currentUnpaidBalance + currentBalance, delta)
            else:
                currentBalance_lbl = currentUnpaidBalance + currentBalance

            draw.text((0, 6), "E", fill='white', font=bitcoinfont)
            draw.text((9, 5), "{:.8f}".format(currentBalance_lbl), fill='white', font=font2)
            draw.text((80, 5), "£{:.2f}".format(usdgbp * currentBalance_lbl), fill='white', font=font2)

            draw.text((0, 32-13), "Estimated Withdrawl Date", fill='white', font=font)
            draw.text((0, 32-6), "{:%a %d %b %H:%M}".format(est_time_withdrawal), fill='white', font=font)

        if displayToShow == 2:

            draw.text((0, -1), "Unpaid Mining Balance", fill='white', font=font)

            if config.SHOW_INTERPOLATED_VALUE:
                unpaidBalance_lbl = lerp(previousUnpaidBalance, currentUnpaidBalance, delta)
            else:
                unpaidBalance_lbl = currentUnpaidBalance + currentBalance

            draw.text((0, 6), "E", fill='white', font=bitcoinfont)
            draw.text((9, 5), "{:.8f}".format(unpaidBalance_lbl), fill='white', font=font2)
            draw.text((80, 5), "£{:.2f}".format(usdgbp * unpaidBalance_lbl), fill='white', font=font2)

            draw.text((0, 32-13), "Next Payout Date", fill='white', font=font)
            draw.text((0, 32-6), "{0}".format(nextAvailablePayout), fill='white', font=font)

        # Experimental display Graph of MH/s over time
        # if displayToShow == 4:

        #     if len(speedData) > 14:                
        #         speedData.pop(0)
        #         print(len(speedData))

        #     speedData.append(lerp(previousTotalAcceptedSpeed, currentTotalAceptedSpeed, delta))

        #     draw.text((0, -1), "Accepted Speed History", fill='white', font=font)
        #     line_points = [(0, 0)] * 15

        #     print(speedData)

        #     for i in range(len(speedData)):
        #         # hard coded MH/s min/max to plot the current accepted speed
        #         normalised = inverse_lerp(28, 32, speedData[i])
        #         lerped = lerp(32-7, 7, normalised)
        #         line_points[i] = (((128 / 14) * i, lerped))

        #     draw.line(line_points, width=2, fill="white", joint='curve')
        #     draw.text((64, 32-6), "{:.2f} MH/s".format(lerp(previousTotalAcceptedSpeed, currentTotalAceptedSpeed, delta)), fill='white', font=font)

    '''
    # FPS COUNTER
    fps = "FPS: {0:0.3f}".format(1/(time.time() - fpsCheck))
    fpsCheck = time.time()
    draw.text((75, 0), fps, fill="white", font=font)
    '''

    if config.RUN_EMULATOR:
        # Virtual display
        npImage = np.asarray(image)
        frameBGR = cv2.cvtColor(npImage, cv2.COLOR_RGB2BGR)
        cv2.imshow('HashAPI', frameBGR)
        k = cv2.waitKey(16) & 0xFF
        if k == 27:
            break
    else:
        # Hardware display
        disp.image(image)
        disp.display()
        time.sleep(1./60)

if config.RUN_EMULATOR:
    # Virtual display
    cv2.destroyAllWindows()
else:
    # Hardware display
    pass
