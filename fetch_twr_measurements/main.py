"""
Quantitec GmbH © 2019

Configure Tags over the air
"""
import base64
import json
import logging
import struct
import os
import argparse
import paho.mqtt.client as mqtt
import copy
import csv
import numpy as np
import random

from sklearn import manifold
from matplotlib import pyplot as plt
from datetime import datetime
from time import sleep, time
from dotenv import load_dotenv
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from google.protobuf.internal.decoder import _DecodeVarint
from requests import Session
from libscrc import kermit

import intranav.proto.inav_full_pb2 as messaging

# Grab configuration from environment variable
API_BASE = os.getenv('API_BASE', 'http://192.168.1.99/api')
API_TOKEN = os.getenv('API_TOKEN',  'j14q5MPpftGBqS6vcTiPb1wIEDPImRBJ')
MQTT_HOST = os.getenv('MQTT_HOST', '192.168.1.99')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER', 'qt_services')
MQTT_PASS = os.getenv('MQTT_PASS', 'VXDY6KeqyTkJ5z8mqZm8')
STARTER_KIT = int(os.getenv('STARTER_KIT', 0))
CONFIG_TIME = float(os.getenv('CONFIG_TIME', 500.0)) # in ms
TIMEOUT_DEVICES = int(os.getenv('TIMEOUT_DEVICES', 1)) # in seconds
NODE_FILTER = (os.getenv('NODE_FILTER', ''))
NUM_OF_RANGES = int(os.getenv('NUM_OF_RANGES', 30))
HTTP_TIMEOUT = 5.0

FRAME_HEADER_LEN = 6
START_OF_PAYLOAD = 3
END_OF_PAYLOAD = 3
END_OF_CRC = 5

# pars arguemtns
apibase: str
apitoken: str
brokerip: str
brokerport: int
brokeruser: str
brokerpass: str
starterkit: bool = False
nodefilter: str
numberOfRanges: int

def main():
    global apibase, apitoken, brokerip, brokerport, brokeruser, brokerpass, starterkit, twrReportFinished, measuredDistanceList, numberOfRanges, nodes

    mqtt = MqttInterface()
    mqtt.add_twr_report_callback()
    mqtt.run(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS)


class MqttInterface:
    def __init__(self, clientid=None):
        self._mqttc = mqtt.Client(clientid)

    def add_twr_report_callback(self):
        self._mqttc.subscribe("node/01aa2145caf1dd0d/tdoa")
        self._mqttc.message_callback_add("node/01aa2145caf1dd0d/tdoa", self.twr_distance_report_callback)

    def run(self, brokerip, brokerport, brokeruser, brokerpass):
        self._mqttc.username_pw_set(brokeruser, brokerpass)
        try:
            self._mqttc.connect(brokerip, brokerport, 10)
            self._mqttc.loop_forever()
        except:
            exit(1)

    def stop(self):
        self._mqttc.disconnect()
        self._mqttc.loop_stop()

    def twr_distance_report_callback(self, client, userdata, message):
        global numberOfRanges, twrReportFinished, rtlsReportList, nodes
        
        msg = messaging.IntranavMessage()

        buffer = message.payload

        while len(buffer) > FRAME_HEADER_LEN:

            length = len(buffer)

            try:
                while buffer[0] != 0x2:
                    buffer = buffer[1:]
            except IndexError:
                pass

            # Get message size
            msg_size = int.from_bytes(buffer[1:3], byteorder="little")

            # Check if buffer holds whole message
            if len(buffer) < msg_size + FRAME_HEADER_LEN:
                print("Truncated message")
                return

            if buffer[msg_size + FRAME_HEADER_LEN - 1] != 0x3:
                print("Missing STX")
                buffer = buffer[1:]

            # Extract Message and CRC
            payload = buffer[START_OF_PAYLOAD : msg_size + END_OF_PAYLOAD]
            crc = int.from_bytes(
                buffer[msg_size + END_OF_PAYLOAD : msg_size + END_OF_CRC],
                byteorder="little",
            )

            # Do CRC check
            if kermit(payload) != crc:
                print("CRC Checksum fail")
                buffer = buffer[msg_size + FRAME_HEADER_LEN :]
                continue

            buffer = buffer[msg_size + FRAME_HEADER_LEN :]

            message_length, field_length = _DecodeVarint(payload, 0)

            # generate a temp buffer for this message define by the length we just decoded
            message_buffer = payload[field_length:(field_length + message_length)]

            try:
                # decode the message
                msg.ParseFromString(message_buffer)
            except:
                pass

            if msg.WhichOneof("msg") != "rtls_report_twr":
                print("received message is not a rtls_report_twr message!")
                #return
            else:

                measurement = {}

                measurement["twr_distance_report"] = msg.rtls_report_twr.twr_distance_report
                measurement["range_number"] = msg.rtls_report_twr.range_number
                measurement["curr_distance"] = msg.rtls_report_twr.curr_distance
                measurement["initiator_addr"] = msg.rtls_report_twr.initiator_addr
                measurement["responder_addr"] = msg.rtls_report_twr.responder_addr

                distance_report = ''
                
                if measurement['twr_distance_report'] == msg.rtls_report_twr.RTLS_TWR_DISTANCE_RESULT_ERROR:
                    distance_report = 'ERROR'
                elif measurement['twr_distance_report'] == msg.rtls_report_twr.RTLS_TWR_DISTANCE_RESULT_SUCCESS:
                    distance_report = 'SUCCESS'
                elif measurement['twr_distance_report'] == msg.rtls_report_twr.RTLS_TWR_DISTANCE_RESULT_TIMEOUT:
                    distance_report = 'TIMEOUT'
                elif measurement['twr_distance_report'] == msg.rtls_report_twr.RTLS_TWR_DISTANCE_RESULT_UNKNOWN:
                    distance_report = 'UNKNOWN'

                initAddr = str(hex(measurement['initiator_addr'])).replace('0x', '')
                respAddr = str(hex(measurement['responder_addr'])).replace('0x', '')

                measurement['curr_distance']

                # temporary code uid of the initiator and the responder are 32 Bit long.
                # so i need to finde the last 8 hex charakter in the twr report and replace them
                # with the uid extracted from the api. 
                for node in nodes:
                    if initAddr in node['uid']:
                        initAddr = node['uid']
                    if respAddr in node['uid']:
                        respAddr = node['uid']
                
                # temporary 

                # save all raw data in a csv file
                cota.write.writerow([initAddr, respAddr, measurement['range_number'], distance_report, measurement['curr_distance']])
                # save all measurements in list
                # only accept successful measuremnts as valide measurment
                rtlsReportList.append({'initiator_addr' : initAddr, 'responder_addr' : respAddr, 'range_number' : measurement['range_number'], 'twr_distance_report' : distance_report, 'curr_distance' : measurement['curr_distance']})
            
                print(f"range_num:{measurement['range_number']} distance:{measurement['curr_distance']}")

                if measurement['range_number'] == numberOfRanges:
                    twrReportFinished = True


    def remove_twr_report_callback(self, node):
        self._mqttc.unsubscribe("node/"+ node['uid'] +"/tdoa")
        self._mqttc.message_callback_remove("node/"+ node['uid'] +"/tdoa")

    def reboot_node(self, node):
        topic = "node/" + node['uid'] + "/cmd"
        self._mqttc.publish(topic, payload='{"cmd":"reboot_hard"}')
        sleep(0.1)

    def twr_initNode(self, node):
        topic = "node/" + node['uid'] + "/cmd"
        self._mqttc.publish(topic, payload='{"type": "config", "rfChan": 5, "rfDatarate": 2,"rfPac": 0, "rfCode": 9, "rfPlen": 20, "rfPrf": 2, "rfTxAntDelay": 16454, "rfRxAntDelay": 16454, "rfNsSfd": 0}')
        sleep(0.1)

    def twr_responder(self, initiator_node, responder_node):
        topic = "node/" + responder_node['uid'] + "/cmd"
        self._mqttc.publish(topic, payload='{"cmd": "twr_responder", "initiator": "'+ initiator_node['uid'] +'", "responder": "'+ responder_node['uid'] +'"}')
        sleep(0.1)

    def twr_inititator(self, initiator_node, responder_node, num_of_ranges):
        topic = "node/" + initiator_node['uid'] + "/cmd"
        self._mqttc.publish(topic, payload='{"cmd": "twr_initiator", "initiator": "'+ initiator_node['uid'] + '", "responder": "'+ responder_node['uid'] +'", "num_twr_ranges": '+ str(num_of_ranges) +'}')
        sleep(0.1)

    def resetModeToIdle(self, node):
        topic = "node/" + node['uid'] + "/cmd"
        self._mqttc.publish(topic, payload='{"cmd":rtls_start}')
        sleep(0.1)

if __name__ == "__main__":
    logging.info('Starting')

    main()