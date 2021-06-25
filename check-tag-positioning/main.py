"""
Intranav GmbH © 2021
check tag positioning
"""

from config import logging
import json
import sys
from paho.mqtt.client import Client as MQTTClient, MQTTMessage

from config import (
    API_BASE,
    API_TOKEN,
    HTTP_TIMEOUT,
    MQTT_HOST,
    MQTT_PASS,
    MQTT_PORT,
    MQTT_USER,
)

MAX_SIZE = 10

tag = {}


def checkNodeCalculation(uid, position, time, zoneId):

    pass

def on_connect(client: MQTTClient, userdata, flags, rc: int):
    # MQTT connection established callback

    # Subscribe to Topics
    client.subscribe("tag/+/position/2")
    client.message_callback_add("tag/+/position/2", on_position)

    client.subscribe("asset/+/zone/+/exit/2")
    client.message_callback_add("asset/+/zone/+/exit/2", on_zone_exit)

def on_position(client: MQTTClient, userdata, message: MQTTMessage):

    try:
        msg = json.loads(message.payload)

        if msg['id'] not in tag:
            tag[msg['id']] = {'buffer': [{'pos': msg['pos'],
                                        'timeStemp': msg['time'],
                                        'tdoadebug': msg['tdoadebug']}]}
        else:
            if len(tag[msg['id']]['buffer']) > MAX_SIZE:
                tag[msg['id']]['buffer'].pop(0)
                tag[msg['id']]['buffer'].append({'pos': msg['pos'],
                                                'timeStemp': msg['time'],
                                                'tdoadebug': msg['tdoadebug']})
            else:
                tag[msg['id']]['buffer'].append({'pos': msg['pos'],
                                                'timeStemp': msg['time'],
                                                'tdoadebug': msg['tdoadebug']})
    except:
        return

def on_zone_exit(client: MQTTClient, userdata, message: MQTTMessage):

    try:
        msg = json.loads(message.payload)
        if msg['uid'] in tag:
            # on exit of zone check 
            if msg['event'] == 'exit':
                checkNodeCalculation(msg['uid'], msg['position'], msg['time'], msg['zoneId'])
                tag[msg['uid']].update({'exitEvent': {'pos': msg['position'],
                                    'exitTime': msg['time'],
                                    'zoneId': msg['zoneId']}})
    except:
        return

def main():
    pass

if __name__ == "__main__":

    # Setup MQTT Client
    MQTT_CLIENT = MQTTClient()
    MQTT_CLIENT.username_pw_set(MQTT_USER, MQTT_PASS)

    # Register MQTT Callbacks
    MQTT_CLIENT.on_connect = on_connect

    try:
        MQTT_CLIENT.connect(MQTT_HOST, MQTT_PORT)
        MQTT_CLIENT.loop_forever()
    except (ConnectionError, OSError) as exc:
        logging.warning(f"Failed to connect to MQTT: {exc}")
        sys.exit(1)