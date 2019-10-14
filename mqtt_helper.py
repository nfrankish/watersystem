import json

RELAY_CONFIG_TOPIC= "homeassistant/switch/irrigation/zone%d/config"
RELAY_COMMAND_TOPIC= "homeassistant/switch/irrigation/zone%d/set"
RELAY_STATE_TOPIC= "homeassistant/switch/irrigation/zone%d/state"

USAGE_CONFIG_TOPIC= "homeassistant/sensor/irrigation/zone%d/total_usage/config"
USAGE_STATE_TOPIC= "homeassistant/sensor/irrigation/zone%d/state"

FLOW_CONFIG_TOPIC= "homeassistant/sensor/irrigation/zone%d/flow_rate/config"
FLOW_STATE_TOPIC= "homeassistant/sensor/irrigation/zone%d/state"

def get_relay_command_topic(zone_id):
    return RELAY_COMMAND_TOPIC % zone_id

def get_relay_config_topic(zone_id):
    return RELAY_CONFIG_TOPIC % zone_id

def get_relay_state_topic(zone_id):
    return RELAY_STATE_TOPIC % zone_id



def _generate_configuration_json_payload(device_class,name,state_topic,unit_of_measurement,value_template):
    payload_setup = {}
    payload_setup['device_class'] = device_class
    payload_setup['name'] = name
    payload_setup['state_topic'] = state_topic
    payload_setup['unit_of_measurement'] = unit_of_measurement
    payload_setup['value_template'] = value_template
    return json.dumps(payload_setup)


