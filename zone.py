import threading

import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Zone(threading.Thread):
    def __init__(self,zone_id,relay_pin,sensor_pin):
        super().__init__()
        self.zone_id = zone_id
        self.relay_pin = relay_pin
        self.sensor_pin = sensor_pin
        self._water_counter = 0
        self.liters_used = 0
        self.flow_rate = 0
        self.watering = 0
        self._stop = threading.Event()
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.HIGH)
        # setting up the sensor pin
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.sensor_pin, GPIO.RISING, callback=self.pulse_counter)

    def pulse_counter(self,channel):
        self._water_counter += 1

    def water_used_in_liters(self):
        return self.liters_used
    def start_watering(self):
        logging.debug("Thread for zone %d asked to start watering" % (i.zone_id))
        GPIO.output(self.relay_pin,GPIO.LOW)
        self.watering = 1

    def stop_watering(self):
        logging.debug("Thread for zone %d asked to stop watering" % (i.zone_id))
        GPIO.output(self.relay_pin, GPIO.HIGH)
        self.watering = 0

    def stop(self):
        self.stop_watering()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            if self.stopped():
                logging.debug("Thread for zone %d asked to stop" % (i.zone_id))
                return
            stamp1 = self._water_counter
            time.sleep(1)
            stamp2 = self._water_counter
            pps = (abs(stamp1 - stamp2))
            self.liters_used = self.liters_used + pps / (5 * 60)
            self.flow_rate = pps / (5 * 60)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    i = Zone(1, 14, 17)
    try:
        i.start()
        count =0
        while True:
            count += 1
            time.sleep(5)
            logging.debug("Zone %d - State %s - CurrentFlow %f - TotalVolume %f" % (i.zone_id, i.watering, i.flow_rate,i.water_used_in_liters()))
            if count == 10:
                i.start_watering()
            if count == 20:
                i.stop_watering()
            if count == 30:
                i.start_watering()
    except:
        print("exception occured")
    finally:
        i.stop_watering()
        i.join()
        GPIO.cleanup()