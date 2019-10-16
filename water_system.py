import mqtt_helper
from zone import Zone
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
from collections import OrderedDict
import logging


zones = []
sensors = OrderedDict([
    ("TotalWaterUsed", dict(name="TotalWaterUsed",name_pretty="Total Water Consumed",typeformat='%f', unit="L", device_class="")),
    ("CurrentCycleRemaining", dict(name="CurrentCycleRemaining",name_pretty="Time Remaining in Cycle",typeformat='%', unit="L", device_class="")),
    ("CurrentFlowRate", dict(name="CurrentFlowRate",name_pretty="Water Flow Rate",typeformat='%f', unit="L/m", device_class=""))



])
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
    global zones
    GPIO.setmode(GPIO.BCM)
    zones.append(Zone(1,14,17))

def mqtt_setup():
    global mqttc, zones
    mqttc.connect(MQTT_HOST,MQTT_PORT)
    mqttc.on_message=on_message
    mqttc.loop_start()
    for z in zones:
        mqttc.publish(mqtt_helper.get_relay_config_topic(z.zone_id), mqtt_helper.generator_relay_configuration_json_payload(z.zone_id), retain=True)
        mqttc.subscribe(mqtt_helper.get_relay_command_topic(z.zone_id))

if __name__ == '__main__':
    setup()
    mqtt_setup()
    for zone in zones:
        zone.start()
    try:
        while True:

            for i,zone in enumerate(zones):
                logging.debug("Looping zone %d" % (zone.zone_id))
                if not zone.is_alive():
                    logging.info("Zone %d exited for some reason - Respawning it" % (zone.zone_id))
                    zones[i] = Zone(zone.zone_id,zone.relay_pin,zone.sensor_pin)
                else:
                    logging.debug("zomg bbq come back here")

            time.sleep(30)
    except:
        logging.debug("I died in a horrible way and i dont know why or how yet")
    finally:
        try:
            for zone in zones:
                zone.stop_watering()
                if zone.is_alive():
                    zone.stop()
                    zone.join()
        except:
            logging.info("Something errored")
        finally:
            GPIO.cleanup()
            logging.info("Finished shutting down - Time to exit the main thread")
