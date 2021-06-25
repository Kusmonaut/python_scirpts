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

from sklearn import manifold
from matplotlib import pyplot as plt
from datetime import datetime
from time import sleep, time
from dotenv import load_dotenv
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from google.protobuf.internal.decoder import _DecodeVarint
from requests import Session
from netaddr import eui64_bare, EUI, eui64_unix_expanded
from libscrc import kermit

import intranav.proto.inav_full_pb2 as messaging
from intranav.constants.devices import (
    NODE_UID_PROP_ID,
    NODE_X_PROP_ID,
    NODE_Y_PROP_ID,
    NODE_Z_PROP_ID,
    NODE_DHCP_PROP_ID,
    NODE_IP_PROP_ID,
    NODE_NETMASK_PROP_ID,
    NODE_GATEWAY_PROP_ID,
    NODE_CONFIGURED_PROP_ID,
    NODE_TYPE_PROP_ID,
    NODE_CCP_DELAY_PROP_ID,
    NODE_MASTER_TO_FOLLOW_PROP_ID,
    NODE_MASTERS_PROP_ID,
    NODE_FLOOR_PROP_ID,
    NODE_PROFILE_PROP_ID,
    NODE_FIRMWARE_PROP_ID,
    NODE_REBOOT_PROP_ID,
    NODE_RESET_PROP_ID,
    NODE_SWITCH_PROP_ID,
    NODE_DEVICE_TYPE_ID
)
# from intranav.constants.status import (
#     UNKNOWN,
#     ONLINE,
#     OFFLINE,
#     BATTERY_LOW,
#     BATTERY_EMPTY,
#     NEW_DEVICE,
#     WARNING,
#     MOVED,
#     SHOCKED
# )

# Load .env file if present
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG if os.getenv('ENV') == 'dev' else logging.INFO,
                    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s')

# Variables you can decide to which mqtt broker you want to connect
twrReportFinished: bool = False
initiatorNode: None
responderNode: None
measuredDistanceList = []
nodeList = []

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
initiator_twr_report_list = []
num_of_successful_ranges = 0

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

DECA_TIME_UNIT = 1.0/499.2e6/128.0 # in s
PAYLOAD_FORMAT = '<BHBBHHIHH' #'<BHBBQ5sHBHHhhhLHBBHB'
PAYLOAD_LENGTH = struct.calcsize(PAYLOAD_FORMAT)

FRAME_HEADER_LEN = 6
START_OF_PAYLOAD = 3
END_OF_PAYLOAD = 3
END_OF_CRC = 5

def configure_logging():
    global log

    log = logging.getLogger("Main")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.setLevel(logging.INFO)
    log.addHandler(handler)

def parse_arguments():
    global apibase, apitoken, brokerip, brokerport, brokeruser, brokerpass, starterkit, nodefilter, numberOfRanges

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--base",
        type=str,
        default=API_BASE,
        help="The API base of IntraNav",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        default=API_TOKEN,
        help="The API token of IntraNav",
    )
    parser.add_argument(
        "-m",
        type=str,
        default=MQTT_HOST,
        help="mqtt broker ip (default: 192.168.1.99)",
        metavar=("IP"),
    )
    parser.add_argument(
        "-p",
        type=int,
        default=MQTT_PORT,
        help="mqtt broker port (default: 1883)",
        metavar=("Port"),
    )
    parser.add_argument(
        "--user",
        type=str,
        default=MQTT_USER,
        help="mqtt broker username (default: qt_internal)",
        metavar=("username"),
    )
    parser.add_argument(
        "--passwd",
        type=str,
        default=MQTT_PASS,
        help="mqtt broker password",
        metavar=("password"),
    )
    parser.add_argument(
        "-s",
        "--starter",
        type=int,
        default=STARTER_KIT,
        help="set 1 for starter Kit (defaul twr: 0)",
        metavar=("starterkit")
    )
    parser.add_argument(
        "-f",
        "--filter",
        nargs='*',
        default=NODE_FILTER,
        help="set 0 for unsing only specific nodes (defaul filter: 0)",
        metavar=("Nodefilter")
    )
    parser.add_argument(
        "-n",
        type=int,
        default=NUM_OF_RANGES,
        help="number of twr reports (default: 30)",
        metavar=("number of ranges"),
    )

    args = parser.parse_args()

    apibase = args.base
    apitoken = args.token
    brokerip = args.m
    brokerport = args.p
    brokeruser = args.user
    brokerpass = args.passwd
    starterkit = args.starter
    nodefilter = args.filter
    numberOfRanges = args.n

def seperate_inactiveNodes(nodes, nodeUIDList):
    _nodesList = []

    for node in nodes:
        if node['uid'] in nodeUIDList:
            _nodesList.append(node)

    return _nodesList


def main():
    
    configure_logging()

    api = None
    apiNodeList = []
    nodeFilterList = {'01aa2145cae48a04', '01aa2145ca141c2d', '01aa2145ca144288', '01aa2145ca141bbb', '01aa2145ca141c94'}

    api = apiInterface()

    apiNodeList = api.get_allNodes()

    nodeList = filter_ndoes(apiNodeList, nodeFilterList)

    calc_euclidean_distance(nodeList)

    pass

def filter_ndoes(nodes, filter):
    result = []

    for node in nodes:
        if node['uid'] not in filter:
            result.append(node)

    return result

def calc_euclidean_distance(nodes):
    temp = nodes
    result = []
    distance = 0

    for node1 in nodes:

        uid1 = node1['uid']
        x1 = node1['x']
        y1 = node1['y']

        for node2 in nodes:
            
            if (nodes.index(node2) >= nodes.index(node1)):
                uid2 = node2['uid']
                x2 = node2['x']
                y2 = node2['y']

                distance = np.sqrt(abs(x2- x1)**2 + abs(y2 - y1)**2)

                result.append([uid1, uid2, distance])
 
    return result


class apiInterface:
    def __init__(self, clientid=None):

        self._nodelist = []

        # to filter only the devicese that are currenctly used for twr
        self._node_filter_list = {'01aa2145ca144109', '01aa2145ca141d05', '01aa2145ca144429', '01aa2145ca141d88'}

    def get_allNodes(self):
        global apibase, apitoken
        s = Session()
        s.headers.update({ 'Authorization': 'Api-Key {}'.format(apitoken) })

        node_config = None
        node = None
        nodes = None
        node_prop = None
        nodes_props = []

        node_config = s.get('{}/devices?type=node&='.format(apibase), timeout=HTTP_TIMEOUT)
        n = {}
        #get nodes as json objekt
        nodes = node_config.json()
        for node in nodes:

            n = {}

            for prop in node.get("properties", []):
                if prop["propId"] == NODE_UID_PROP_ID:
                    n['uid'] = prop['value']
                if prop["propId"] == NODE_X_PROP_ID:
                    n['x'] = int(prop['value'])
                if prop["propId"] == NODE_Y_PROP_ID:
                    n['y'] = int(prop['value'])
                if prop["propId"] == NODE_Z_PROP_ID:
                    n['z'] = int(prop['value'])

            self._nodelist.append(n)

        return self._nodelist

    def filterNodes(self, nodes):
        tempNodes = []

        for node in nodes:
            if node['uid'] in self._node_filter_list:
                tempNodes.append(node)
        return tempNodes

    def update_state(self, id, uid, x_position, y_position):
        global apibase, apitoken
        s = Session()
        s.headers.update({"Authorization": "Api-Key {}".format(apitoken)})
        req_body = {
            "typeId": NODE_DEVICE_TYPE_ID,
            "properties": [
                {"value": str(x_position), "propId": NODE_X_PROP_ID},
                {"value": str(y_position), "propId": NODE_Y_PROP_ID},
            ],
        }
        req = s.patch(f"{apibase}/devices/{id}", json=req_body)

        if not req.ok:
            logging.error("Failed to update Node %s: %i", uid, req.status_code)


if __name__ == "__main__":
    logging.info('Starting')
    
    parse_arguments()

    main()
