import mqtt_helper
from zone import Zone
import threading
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import logging

zones =[]
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
MQTT_HOST = 'hass.home.our-lan.com'
MQTT_PORT = 1883

mqttc = mqtt.Client("Irrigation_system")

def on_message(client, userdata, message):
    logging.debug("message received " + str(message.payload.decode("utf-8")))
    logging.debug("message topic="+message.topic)
    logging.debug("message qos="+message.qos)
    logging.debug("message retain flag="+message.retain)

def setup():
    GPIO.setmode(GPIO.BCM)
    zones.append(Zone(1,14,17))

def mqtt_setup():
    mqttc.connect(MQTT_HOST,MQTT_PORT)
    mqttc.on_message=on_message
    mqttc.loop_start()
    for zone in zones:
        mqttc.subscribe()

if __name__ == '__main__':
    setup()
    mqtt_setup()
    for zone in zones:
        zone.start()



