#! /usr/bin/env python

import drivers
from time import sleep
from datetime import datetime
import threading
from queue import Queue
from lib import RotaryEncoder, fillUpLine, generateRatioStrenthLine
import RPi.GPIO as GPIO
from time import sleep
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

ratio = 16
ratioEditable = True
display.lcd_display_extended_string(generateRatioStrenthLine(ratio), 2)


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
    display.lcd_clear
    if(currentScreen == CurrentScreen.STRENGTH):
        ratioEditable = False
        currentScreen = CurrentScreen.PLACE_BEAN_HOLDER
        display.lcd_display_extended_string("leere Bohnendose",1)
        display.lcd_display_extended_string("auf Wage stellen",2)
    elif(currentScreen == CurrentScreen.PLACE_BEAN_HOLDER):
        currentScreen = CurrentScreen.PLACE_FILLED_BEAN_HOLDER
        display.lcd_display_extended_string("F{0xF5}llen & wiegen ",1)
        display.lcd_display_extended_string("60g             ",2)
    elif(currentScreen == CurrentScreen.PLACE_FILLED_BEAN_HOLDER):
        currentScreen = CurrentScreen.PLACE_COFFEE_CAN
        display.lcd_display_extended_string("leere Karaffe   ",1)
        display.lcd_display_extended_string("auf Wage stellen",2)
    elif(currentScreen == CurrentScreen.PLACE_COFFEE_CAN):
        currentScreen = CurrentScreen.FILL_COFFEE_CAN
        display.lcd_display_extended_string("1000/1200ml     ",1)
        display.lcd_display_extended_string("{0xFF}{0xFF}{0xFF}{0xFF}{0xFF}{0xD0}{0xD0}{0xD0}{0xD0}{0xD0}xxxxxx",2)
    elif(currentScreen == CurrentScreen.PLACE_FILLED_BEAN_HOLDER):
        currentScreen = CurrentScreen.PLACE_FILLED_BEAN_HOLDER
        display.lcd_display_extended_string("fullen & wiegen ",1)
        display.lcd_display_extended_string("60g             ",2)
    elif(currentScreen == CurrentScreen.FILL_COFFEE_CAN):
        currentScreen = CurrentScreen.STRENGTH;
        ratioEditable = True
        display.lcd_display_extended_string('Verh. | St{0xE1}rke', 1)
        display.lcd_display_extended_string(generateRatioStrenthLine(ratio), 2)



def main():
    try:
        RotaryEncoder(ROTARY_PIN_A, ROTARY_PIN_B, callback=on_turn, buttonPin=ROTARY_PIN_BUTTON, buttonCallback=on_press)
        while True :
            sleep(.01)
            EVENT.wait(1000)
            consume_queue()
            EVENT.clear()

    except KeyboardInterrupt: # Ctrl-C to terminate the program
        print('Cleanup')
        GPIO.cleanup()
        display.lcd_clear()


if __name__ == '__main__':
    main()