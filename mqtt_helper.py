import json
import re

RELAY_CONFIG_TOPIC= "homeassistant/switch/irrigation/zone%d/config"
RELAY_COMMAND_TOPIC= "homeassistant/switch/irrigation/zone%d/set"
RELAY_COMMAND_TOPIC_REGEX = "homeassistant\/switch\/irrigation\/zone(\d)\/set"

RELAY_STATE_TOPIC= "homeassistant/switch/irrigation/zone%d/state"

SENSOR_CONFIG_TOPIC= "homeassistant/sensor/zone%d/%s/config"
SENSOR_STATE_TOPIC= "homeassistant/sensor/irrigation/zone%d/state"


def get_relay_command_topic(zone_id):
    return RELAY_COMMAND_TOPIC % zone_id

def get_relay_config_topic(zone_id):
    return RELAY_CONFIG_TOPIC % zone_id

def get_relay_state_topic(zone_id):
    return RELAY_STATE_TOPIC % zone_id

def get_zone_from_relay_topic(topic):
    match = re.search(RELAY_COMMAND_TOPIC_REGEX,topic)
    return match.group(1)

def get_sensor_config_topic(zone_id,sensor):
    return SENSOR_CONFIG_TOPIC % (zone_id,sensor)

def get_sensor_state_topic(zone_id):
    return SENSOR_STATE_TOPIC % zone_id



def generate_sensor_configuration_json_payload(zone_id, name,unit_of_measurement,value_template,device_class = None):
    payload_setup = {}
    payload_setup['name'] = name
    payload_setup['state_topic'] = get_sensor_state_topic(zone_id)
    payload_setup['unit_of_measurement'] = unit_of_measurement
    #payload_setup['value_template'] = value_template
    if not device_class is None:
        payload_setup['device_class'] = device_class
    return json.dumps(payload_setup)

def generator_relay_configuration_json_payload(zone_id):
    payload_setup = {}
    payload_setup['name'] = 'Zone %d' % (zone_id)
    payload_setup['command_topic'] = get_relay_command_topic(zone_id)
    payload_setup['state_topic'] = get_relay_state_topic(zone_id)
    payload_setup['icon'] ="mdi:water-pump"
    json_msg = json.dumps(payload_setup)
    return json_msg
