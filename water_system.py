import mqtt_helper
from zone import Zone
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time, json
from collections import OrderedDict
import logging


zones = []
sensors = OrderedDict([
    ("TotalWaterUsed", dict(name="TotalWaterUsed",name_pretty="Total Water Consumed",typeformat='%f', unit="L", device_class="water",icon="mdi:water")),
    ("CurrentCycleRemaining", dict(name="CurrentCycleRemaining",name_pretty="Time Remaining in Cycle",typeformat='%', unit="", device_class="timer",icon="mdi:timer")),
    ("CurrentFlowRate", dict(name="CurrentFlowRate",name_pretty="Water Flow Rate",typeformat='%f', unit="L/s", device_class="water",icon="mdi:water-pump"))



])
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
MQTT_HOST = 'hass.home.our-lan.com'
MQTT_PORT = 1883
STATE_FILE= "states.json"

mqttc = mqtt.Client("Irrigation_system")

def on_message(client, userdata, message):
    global zones
    zid = int(mqtt_helper.get_zone_from_relay_topic(message.topic))
    for z in zones:
        if z.zone_id == zid:
            z.set_state(message.payload.decode("utf-8"))
            mqttc.publish(mqtt_helper.get_relay_state_topic(z.zone_id).lower(), z.get_state(),retain=True)
            break

def setup():
    global zones
    GPIO.setmode(GPIO.BCM)
    data = []
    try:
        with open(STATE_FILE) as json_file:
            data = json.load(json_file)
    except:
        logging.debug("State file not available - ignoring")
    print(data)
    if str(1) in  data:
        logging.info("State file found for zone %d - Value %f" % (1,data[str(1)]))
        zones.append(Zone(1,14,17,data[str(1)]))
    else:
        zones.append(Zone(1, 14, 17))



def mqtt_setup():
    global mqttc, zones, sensors
    mqttc.connect(MQTT_HOST,MQTT_PORT)
    mqttc.on_message=on_message
    mqttc.loop_start()
    for z in zones:
        mqttc.publish(mqtt_helper.get_relay_config_topic(z.zone_id), mqtt_helper.generator_relay_configuration_json_payload(z.zone_id), retain=True)
        mqttc.subscribe(mqtt_helper.get_relay_command_topic(z.zone_id))

        for sensor, params in sensors.items():
            payload = {}
            payload['state_topic'] = mqtt_helper.get_sensor_state_topic(z.zone_id).lower()
            payload['unit_of_measurement'] = params['unit']
            payload['value_template'] = "{{ value_json.%s }}" % (sensor,)
            payload['name'] = "Zone {} - {}".format(z.zone_id, sensor.title())
            payload['icon'] = params['icon']

            if 'device_class' in params:
         #       payload['device_class'] = params['device_class']
                logging.debug("ignoring device_class")
            logging.debug(json.dumps(payload))
            logging.debug(mqtt_helper.get_sensor_config_topic(z.zone_id,sensor))
            mqttc.publish(mqtt_helper.get_sensor_config_topic(z.zone_id,sensor).lower(), json.dumps(payload),retain=True)


if __name__ == '__main__':
    setup()
    mqtt_setup()
    for zone in zones:
        zone.start()
    try:
        while True:
            state = {}
            for i,zone in enumerate(zones):
                logging.debug("Looping zone %d" % (zone.zone_id))
                if not zone.is_alive():
                    logging.error("Zone %d exited for some reason - Respawning it" % (zone.zone_id))
                    zones[i] = Zone(zone.zone_id,zone.relay_pin,zone.sensor_pin,zone.water_used_in_liters())
                else:
                    sensor_data = {"TotalWaterUsed": zone.water_used_in_liters(), "CurrentCycleRemaining": zone.get_time_remaining(),
                            "CurrentFlowRate": zone.flow_rate}
                    mqttc.publish(mqtt_helper.get_sensor_state_topic(zone.zone_id).lower(), json.dumps(sensor_data), retain=True)
                    mqttc.publish(mqtt_helper.get_relay_state_topic(zone.zone_id).lower(),zone.get_state(), retain=True)
                    state[zone.zone_id] = zone.water_used_in_liters()
            try:
                with open(STATE_FILE, 'w') as outfile:
                    json.dump(state,outfile)
            except:
                logging.debug("Couldnt write file, but not caring")
            time.sleep(5)
    except Exception as e:
        logging.error("I died in a horrible way and i dont know why or how yet")
        logging.error(str(e))
    finally:
        try:
            for zone in zones:
                zone.stop_watering()
                if zone.is_alive():
                    zone.stop()
                    zone.join()
        except Exception as e:
            logging.error("Something errored")
            logging.error(str(e))
        finally:
            GPIO.cleanup()
            logging.info("Finished shutting down - Time to exit the main thread")
