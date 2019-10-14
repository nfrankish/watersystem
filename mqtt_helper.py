
RELAY_CONFIG_TOPIC= "homeassistant/switch/irrigation/zone%d/config"
RELAY_COMMAND_TOPIC= "homeassistant/switch/irrigation/zone%d/set"
RELAY_STATE_TOPIC= "homeassistant/switch/irrigation/zone%d/state"

def get_relay_command_topic(zone_id):
    return RELAY_COMMAND_TOPIC % zone_id

def get_relay_config_topic(zone_id):
    return RELAY_CONFIG_TOPIC % zone_id

def get_relay_state_topic(zone_id):
    return RELAY_STATE_TOPIC % zone_id




