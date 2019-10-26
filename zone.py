import threading

import RPi.GPIO as GPIO
import time
import logging
from datetime import datetime,timedelta
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Zone(threading.Thread):

    def __init__(self,zone_id,relay_pin,sensor_pin, water_used=0):
        super().__init__()
        self.zone_id = zone_id
        self.relay_pin = relay_pin
        self.sensor_pin = sensor_pin
        self._water_counter = 0
        self.liters_used = water_used
        self.flow_rate = 0
        self.watering = 0
        self._stopper = threading.Event()
        self._start_time = datetime.now()
        self._stop_time = datetime.now()
        self._maximum_run_time = 5

        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.HIGH)
        # setting up the sensor pin
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.sensor_pin, GPIO.RISING, callback=self._pulse_counter)

    def _pulse_counter(self,channel):
        self._water_counter += 1

    def water_used_in_liters(self):
        return self.liters_used
    def start_watering(self):
        logging.debug("Thread for zone %d asked to start watering" % (self.zone_id))
        GPIO.output(self.relay_pin,GPIO.LOW)
        self.watering = 1
        self._start_time = datetime.now()

    def stop_watering(self):
        logging.debug("Thread for zone %d asked to stop watering" % (self.zone_id))
        GPIO.output(self.relay_pin, GPIO.HIGH)
        self._stop_time = datetime.now()

        self.watering = 0

    def get_state(self):
        if self.watering:
            return 'ON'
        else:
            return 'OFF'
    def set_state(self, state):
        logging.debug("Setting state to %s" % state)
        if state == "ON":
            self.start_watering()
        if state == "OFF":
            self.stop_watering()


    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def _calculate_water(self):
        stamp1 = self._water_counter
        time.sleep(1)
        stamp2 = self._water_counter
        pps = (abs(stamp1 - stamp2))
        self.liters_used = self.liters_used + pps / (5 * 60)
        self.flow_rate = pps / (5 * 60)

    def get_time_remaining(self):
        if self.watering == 0:
            return str(0)
        else:
            now = datetime.now()
            diff =  (self._start_time+timedelta(minutes=self._maximum_run_time)) - now
            return str(diff)


    def run(self):
        while not self.stopped():
            self._calculate_water()
            logging.debug("Zone %d - State %s - CurrentFlow %f - TotalVolume %f - Time Remainding %s "% (
            self.zone_id, self.watering, self.flow_rate, self.water_used_in_liters(), self.get_time_remaining()))
            now = datetime.now()
            if self.watering == 1 and self._start_time+timedelta(minutes=self._maximum_run_time) < now:
                logging.info("Zone %d reached maximum runtime - Stopping" % (self.zone_id,))
                self.stop_watering()

        if self.watering:
            self.stop_watering()
        logging.debug("Thread for zone %d asked to stop" % (self.zone_id,))



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
            if count == 1:
                i.start_watering()
            if count == 20:
                i.stop_watering()
            if count == 30:
                i.start_watering()
    except:
        print("exception occured")
    finally:
        try:
            i.stop_watering()
            i.join()
        finally:
            GPIO.cleanup()