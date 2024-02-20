#! /usr/bin/env python

import drivers
from datetime import datetime
import threading
from queue import Queue
from lib import RotaryEncoder, fillUpLine, generateRatioStrenthLine, HX711, getTargetWeightFromGroundsWeight, generateFillLine
import RPi.GPIO as GPIO
import time
from enum import Enum

ROTARY_PIN_A = 22
ROTARY_PIN_B = 23
ROTARY_PIN_BUTTON = 27

RATIO_MIN = 1
RATIO_MAX = 36

QUEUE = Queue()
EVENT = threading.Event()


display = drivers.Lcd()
display.lcd_display_extended_string('Verh. | St{0xE1}rke', 1)
referenceUnit1 = -980
hx1 = HX711(26, 16)
hx1.set_reading_format("MSB", "MSB")
hx1.set_reference_unit(referenceUnit1)
hx1.reset()


waterWeight = 0
beansWeight = 0
targetWaterWeight = 0
ratio = 16
ratioEditable = True
display.lcd_display_extended_string(generateRatioStrenthLine(ratio), 2)
lastPressTime = time.time()


class CurrentScreen(Enum):
    STRENGTH=1
    PLACE_BEAN_HOLDER=2
    PLACE_FILLED_BEAN_HOLDER=3
    PLACE_COFFEE_CAN=4
    FILL_COFFEE_CAN=5

currentScreen = CurrentScreen.STRENGTH


def on_turn(delta):
    QUEUE.put(delta)
    EVENT.set()
    
def consume_queue():
    while not QUEUE.empty():
      delta = QUEUE.get()
      handle_delta(delta)
  
def handle_delta(delta):
    global ratio
    global ratioEditable
    if(ratioEditable == False):
       return
    print(str(ratioEditable))
    ratio += delta
    if(ratio > 36):
       ratio = 36
    elif(ratio < 1):
       ratio = 1
    display.lcd_display_extended_string(generateRatioStrenthLine(ratio), 2)

def on_press(param):
    global display
    global currentScreen
    global ratioEditable
    global lastPressTime

    if(lastPressTime - time.time() < 1):
        return
    lastPressTime = time.time()

    display.lcd_clear()
    if(currentScreen == CurrentScreen.STRENGTH):
        ratioEditable = False
        currentScreen = CurrentScreen.PLACE_BEAN_HOLDER
        display.lcd_display_extended_string("leere Bohnendose",1)
        display.lcd_display_extended_string("auf Wage stellen",2)
    elif(currentScreen == CurrentScreen.PLACE_BEAN_HOLDER):
        hx1.tare()
        currentScreen = CurrentScreen.PLACE_FILLED_BEAN_HOLDER
        display.lcd_display_extended_string("F{0xF5}llen & wiegen ",1)
        display.lcd_display_extended_string("60g             ",2)
    elif(currentScreen == CurrentScreen.PLACE_FILLED_BEAN_HOLDER and beansWeight > 1):
        currentScreen = CurrentScreen.PLACE_COFFEE_CAN
        display.lcd_display_extended_string("leere Karaffe   ",1)
        display.lcd_display_extended_string("auf Wage stellen",2)
        time.sleep(1)
        display.lcd_display_extended_string("leere Karaffe   ",1)
        display.lcd_display_extended_string("auf Wage stellen",2)
    elif(currentScreen == CurrentScreen.PLACE_COFFEE_CAN):
        hx1.tare()
        currentScreen = CurrentScreen.FILL_COFFEE_CAN
    elif(currentScreen == CurrentScreen.PLACE_FILLED_BEAN_HOLDER):
        currentScreen = CurrentScreen.PLACE_FILLED_BEAN_HOLDER
        display.lcd_display_extended_string("fullen & wiegen ",1)
        time.sleep(1)
        display.lcd_display_extended_string("fullen & wiegen ",1)

    elif(currentScreen == CurrentScreen.FILL_COFFEE_CAN):
        currentScreen = CurrentScreen.STRENGTH;
        ratioEditable = True
        display.lcd_display_extended_string('Verh. | St{0xE1}rke', 1)
        display.lcd_display_extended_string(generateRatioStrenthLine(ratio), 2)

def doLoadCellCheck():
    global currentScreen
    global beansWeight
    global waterWeight
    global targetWaterWeight
    while(True):
        # Check if the current screen requeires weight
        time.sleep(.25)
        if (currentScreen == CurrentScreen.PLACE_FILLED_BEAN_HOLDER):
            currentWeight = hx1.get_weight(3)
            beansWeight = currentWeight
            targetWaterWeight = getTargetWeightFromGroundsWeight(beansWeight, 1, ratio)
            display.lcd_display_extended_string(str(round(beansWeight, 1)) + "g              ",2)
            print('Beans weight: ' + str(currentWeight) + '. Target weight: ' + str(targetWaterWeight))
        elif currentScreen == CurrentScreen.FILL_COFFEE_CAN:
            currentWeight = hx1.get_weight(3)
            waterWeight = currentWeight
            print('Water weight: ' + str(currentWeight))
            waterWeightString = str(int(waterWeight)).rjust(4)
            display.lcd_display_extended_string(waterWeightString + "/"+ str(targetWaterWeight) +"ml     ",1)
            display.lcd_display_extended_string(generateFillLine(waterWeight, targetWaterWeight),2)



def main():
    try:
        RotaryEncoder(ROTARY_PIN_A, ROTARY_PIN_B, callback=on_turn, buttonPin=ROTARY_PIN_BUTTON, buttonCallback=on_press)
        loadCellCheck = threading.Thread(target=doLoadCellCheck)
        loadCellCheck.start()
        while True :
            time.sleep(.01)
            EVENT.wait(1000)
            consume_queue()
            EVENT.clear()

    except KeyboardInterrupt: # Ctrl-C to terminate the program
        print('Cleanup')
        GPIO.cleanup()
        display.lcd_clear()


if __name__ == '__main__':
    main()