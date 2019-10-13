import json
import traceback

import requests
import sys
import time
import datetime
import paho.mqtt.client as mqtt
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

MQTT_HOST = 'hass.home.our-lan.com'
MQTT_PORT = 1883

RELAY_CONFIG_TOPIC= "homeassistant/switch/irrigation/zone1/config"
RELAY_COMMAND_TOPIC= "homeassistant/switch/irrigation/zone1/set"
RELAY_STATE_TOPIC= "homeassistant/switch/irrigation/zone1/state"

def on_message(client, userdata, message):
    logging.debug("message received " + str(message.payload.decode("utf-8")))
    logging.debug("message topic="+message.topic)
    logging.debug("message qos="+message.qos)
    logging.debug("message retain flag="+message.retain)

mqttc = mqtt.Client("MQTT_TEST")

try:
    logging.info("Connecting to MQTT on %s:%s"%(MQTT_HOST,MQTT_PORT))
    mqttc.connect(MQTT_HOST,MQTT_PORT)
    mqttc.on_message=on_message
    mqttc.loop_start()
    logging.debug("Subscribing to topic - %s" % RELAY_COMMAND_TOPIC)
    mqttc.publish(RELAY_CONFIG_TOPIC, retain=True)
    mqttc.publish("homeassistant/switch/irrigation/config", retain=True)
    mqttc.subscribe(RELAY_COMMAND_TOPIC)
    subscribe_message = {}
    subscribe_message['name']='GardenTest'
    subscribe_message['command_topic']=RELAY_COMMAND_TOPIC
    subscribe_message['state_topic'] = RELAY_STATE_TOPIC
    json_msg = json.dumps(subscribe_message)
    logging.debug(json_msg)
    mqttc.publish(RELAY_CONFIG_TOPIC, json.dumps(subscribe_message), retain=True)
    while 1:
        continue
except Exception as msg:
    mqttc.disconnect()
    logging.debug(msg)

logging.debug("I still made it here")
##$ mosquitto_pub -h 127.0.0.1 -p 1883 -t "homeassistant/switch/irrigation/config" \
  #-m '{"name": "garden", "command_topic": "homeassistant/switch/irrigation/set", "state_topic": "homeassistant/switch/irrigation/state"}'


