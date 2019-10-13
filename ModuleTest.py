import threading

import RPi.GPIO as GPIO
import time,datetime
import os
#import simplejson
import sys
import json
import math
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#Pin order - Relay,Flow
ZONE_PINS= [[14,17]]

water_counter =0
ppm=0
liters=0.00

def my_callback(channel):
    global water_counter
    water_counter=water_counter+1


def setup():
    logging.debug("GPIO setup")
    GPIO.setmode(GPIO.BCM)
    for zone in range(len(ZONE_PINS)):
        flowpin = ZONE_PINS[zone][1]
        relaypin = ZONE_PINS[zone][0]
        logging.debug("Setting up zone %d - Sensor pin: %d, Relay pin: %d" % (zone,flowpin,relaypin))
        # Setting up the relay pin
        GPIO.setup(relaypin, GPIO.OUT)
        GPIO.output(relaypin, GPIO.LOW)
        # setting up the sensor pin
        GPIO.setup(flowpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(flowpin, GPIO.RISING, callback=my_callback)


def counter():
    logging.debug("Starting counter")
    global water_counter, liters
    while 1:
        stamp1=water_counter
        time.sleep(1)
        stamp2=water_counter
        pps = (abs(stamp1 - stamp2))
        logging.debug("PPS is %d", pps)
        liters = liters + pps / (5 * 60)
   #     print(type(pps))
   #     print(type(liters))
        logging.debug("Litres consumed: %f - PPS is %d" % (liters,pps))

try:
    setup()
    count=100
    w2 = threading.Thread(name='counter', target=counter)
    w2.start()
    for x in range(count):
        logging.debug("Turning relay on..")
        GPIO.output(14,GPIO.LOW)
        time.sleep(5)
        logging.debug("Turning relay off..")
        GPIO.output(14, GPIO.HIGH)
        time.sleep(5)

finally:
    w2.join()
    logging.debug("Cleaning up the GPIO settings")
    GPIO.cleanup()
    logging.debug("exiting..")
