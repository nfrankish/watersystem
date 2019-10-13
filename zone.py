import threading

import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

class Zone:
    def __init__(self,id,relay_pin,sensor_pin):
        self.counterThread = threading.Thread(name='counter', target=self.thread_counter)
        self.id = id
        self.relay_pin = relay_pin
        self.sensor_pin = sensor_pin
        self._water_counter = 0
        self.liters_used = 0
        self.flow_rate = 0
    def setup(self,):
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.LOW)
        # setting up the sensor pin
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.sensor_pin, GPIO.RISING, callback=self.pulse_counter)
        self.counterThread.start()

    def pulse_counter(self,channel):
        self._water_counter += 1

    def water_used_in_liters(self):
        return self.liters_used

    def thread_counter(self):
        while 1:
            stamp1 = self._water_counter
            time.sleep(1)
            stamp2 = self._water_counter
            pps = (abs(stamp1 - stamp2))
            self.liters_used = self.liters_used + pps / (5 * 60)
            self.flow_rate = pps / (5 * 60)