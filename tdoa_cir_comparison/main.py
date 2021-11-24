"""
Intranav GmbH © 2021
check tag positioning
"""

import json
import logging
import os
import time
import sys
import numpy as np
import csv

from collections import defaultdict
from time import time
from typing import Any, Dict, List
from scipy.spatial import distance
from scipy.optimize import least_squares
from PyQt5 import uic, QtGui
from PyQt5.Qt import Qt, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStyleFactory
from requests import RequestException, Session
from paho.mqtt.client import Client as MQTTClient, MQTTMessage

from decode import *
from multilaterate import get_loci
from multilateration import *

from config import (
    HTTP_TIMEOUT,
    COLOR_PALET,
    API_BASE,
    API_TOKEN,
    NODE_FILTER,
    API_ONLINE,
    X_MIN,
    X_MAX,
    Y_MIN,
    Y_MAX,
    SPEED_OF_LIGHT,
    DELTA_D,
    MAX_D,
    MQTT_USER,
    MQTT_PASS,
    MQTT_HOST,
    MQTT_PORT,
    FLOOR_ID,
    TAG_ID,
    PHYSICAL_TAG_POSITION_X,
    PHYSICAL_TAG_POSITION_Y
)

from intranav.proto import Decoder
from intranav.proto.inav_le_pb2 import BlinkCollection, ReportContainer
from intranav.constants.devices import (
    NODE_UID_PROP_ID,
    NODE_X_PROP_ID,
    NODE_Y_PROP_ID,
    NODE_Z_PROP_ID,
    NODE_TYPE_PROP_ID,
    NODE_FLOOR_PROP_ID
)

tag_position: Dict[str ,Any] = defaultdict(dict)
decoders: Dict[int, Decoder] = defaultdict(Decoder)
cache: Dict[int, Dict[int, BlinkCollection]] = defaultdict(dict)

class Window(QMainWindow, QDialog):

    def __init__(self,mqtt_client, tag_id, floors):
        super(Window, self).__init__()
        uic.loadUi("checking-tag-positions.ui", self)

        mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

        mqtt_client.on_connect = self.on_connect

        mqtt_client.connect(MQTT_HOST, MQTT_PORT)
        mqtt_client.loop_start()

        self._floor = floors[FLOOR_ID]

        self.setWindowTitle(f"Tag Analayse for tag_id: {tag_id}")

        self.horizontalSlider.valueChanged.connect(self.update_tag_position)

    def update_tag_position(self):

        node_positions: Dict[str, Any] = {}
        node_diags: Dict[str, Any] = {}

        position = list(tag_position)[self.horizontalSlider.value()]

        self.MplWidget_tdoa.canvas.axes.clear()
        self.MplWidget_cir.canvas.axes.clear()

        self.MplWidget_tdoa.canvas.draw()
        self.MplWidget_cir.canvas.draw()

        if 'tdoadebug' in tag_position[position]:
            hyperbolas = self.create_hyperbola(tag_position[position]['tdoadebug'])

            if not hyperbolas:
                logging.warning("hyperbola creation failed")
                return
            
            node_positions = self.create_Nodes(tag_position[position]['tdoadebug'])
            
            self.draw_on_tdoa_canvas(hyperbolas, node_positions)
        
        if 'blink_collection' in tag_position[position]:

            node_diags = self.create_diagnostics(tag_position[position]['blink_collection'])

            if not node_diags:
                logging.warning("nodes diag creation failed")

            if node_positions:
                self.color_matching(node_positions, node_diags)

                if not node_diags:
                    return

                self.draw_on_diag_canvas(node_diags)

    def color_matching(self, node_positions, node_diags):
        for uid in node_positions:
            if uid != TAG_ID:
                try:
                    if uid in node_diags:
                        node_diags[uid].update({'color': node_positions[uid]['color']})
                except Exception as ex:
                    logging.error(f"error code: {ex}")
        if node_diags:          
            for uid in node_diags:
                if 'color' not in node_diags[uid]:
                    node_diags[uid].update({'color': 'g'})
        else:
            return

    def create_diagnostics(self, blink_collection):
        
        nodes: Dict[int, Any] = {}

        for report in blink_collection.blink_reports:
            uid = "{:016x}".format(report)
            diagnostics = decode_diagnostics(
                blink_collection.blink_reports[report].blink_report.diagnostics.diagnostics,
                report,
                blink_collection.blink_reports[report].blink_report.tag_id,
            )

            if not diagnostics:
                logging.warning(f"length of diagnostics for node does not match [node_id: {report:016x}]")
                continue

            nodes[uid] = {"tag_id": "{:016x}".format(blink_collection.blink_reports[report].blink_report.tag_id)}
            nodes[uid]["diag"] = diagnostics

            delta_peak = calc_peak_difference(diagnostics)

            if delta_peak:
                nodes[uid]["delta"] = delta_peak

            pwr_level = calc_power_level(diagnostics)

            if pwr_level:
                nodes[uid]["pwr_level"] = pwr_level

            pwr_level_delta = calc_power_level_delta(nodes[uid]["pwr_level"])

            if pwr_level_delta:
                nodes[uid]["pwr_level"]["delta"] = pwr_level_delta

        if len(nodes) == 0:
            logging.warning(
                f"No node can be selected from blink reports of size [ len blink_reports: {len(blink_collection.blink_reports)}]"
            )
            return None

        for node in nodes:
            logging.info(
                f"node_id: {node}, fp_power: {nodes[node]['pwr_level']['fp_power']}, rx_power: {nodes[node]['pwr_level']['rx_power']}, fp_index: {nodes[node]['diag']['fp_index']}"
            )
            if nodes[node]["delta"] <= 3.3:
                nodes[node]["prNlos"] = 0
            elif nodes[node]["delta"] < 6 and nodes[node]["delta"] > 3.3:
                nodes[node]["prNlos"] = 0.39178 * nodes[node]["delta"] - 1.31719
            else:
                nodes[node]["prNlos"] = 1

        node_uid = int(list(nodes.keys())[0], 16)
        node_id = get_best_node(
            dict((node, nodes[node]["prNlos"]) for node in nodes),
            "{:016x}".format(blink_collection.blink_reports[node_uid].blink_report.tag_id),
        )

        return nodes

    def draw_on_diag_canvas(self,node_diags):

        for i, node in enumerate(node_diags):
            self.MplWidget_cir.canvas.axes.title.set_text("tag_ID : " + node_diags[node]['tag_id'])
            self.MplWidget_cir.canvas.axes.plot(node_diags[node]['diag']['cir_amplitude'], label=node, color=node_diags[node]['color'], linestyle = '-' if node_diags[node]['prNlos'] < 1 else '--')
            self.MplWidget_cir.canvas.axes.axvline(x = node_diags[node]['diag']['pp_index'] - int(node_diags[node]['diag']['fp_index']) + 10, color=node_diags[node]['color'], linestyle='-.')
            self.MplWidget_cir.canvas.axes.axhline(y = node_diags[node]['diag']['noise_threshold'], color=node_diags[node]['color'], linestyle='-.')
            self.MplWidget_cir.canvas.axes.scatter(y = node_diags[node]['diag']['fp_ampl3'], x = 11, marker='x', color=node_diags[node]['color'])
            self.MplWidget_cir.canvas.axes.scatter(y = node_diags[node]['diag']['fp_ampl2'], x = 12, marker='x', color=node_diags[node]['color'])
            self.MplWidget_cir.canvas.axes.scatter(y = node_diags[node]['diag']['fp_ampl1'], x = 13, marker='x', color=node_diags[node]['color'])
        self.MplWidget_cir.canvas.axes.yaxis.label.set_text('Channel Impulse Response Amplitude')
        self.MplWidget_cir.canvas.axes.xaxis.label.set_text('Sample Index')
        self.MplWidget_cir.canvas.axes.grid(True)
        self.MplWidget_cir.canvas.axes.legend()
        self.MplWidget_cir.canvas.draw()

    def draw_on_tdoa_canvas(self, hyperbolas, node_positions):

        self.MplWidget_tdoa.canvas.axes.clear()

        self.MplWidget_tdoa.canvas.axes.set_xlim(X_MIN, X_MAX)
        self.MplWidget_tdoa.canvas.axes.set_ylim(Y_MIN, Y_MAX)

        for uid in hyperbolas:
            self.MplWidget_tdoa.canvas.axes.plot(hyperbolas[uid]['loci'][0], hyperbolas[uid]['loci'][1], color=hyperbolas[uid]['color'])

        for uid in node_positions:
            self.MplWidget_tdoa.canvas.axes.scatter(node_positions[uid]['x'], node_positions[uid]['y'], zorder=10, s=100, color=node_positions[uid]['color'] , marker=node_positions[uid]['marker'] if node_positions[uid]['marker'] else 'o' )

        self.MplWidget_tdoa.canvas.axes.scatter( PHYSICAL_TAG_POSITION_X, PHYSICAL_TAG_POSITION_Y, s=100, color= 'r', marker='+')

        for node in node_positions:
            self.MplWidget_tdoa.canvas.axes.annotate(
                node,
                xy=(node_positions[node]['x'], node_positions[node]['y']), xytext=(-10, 10),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

        # self.MplWidget_tdoa.canvas.setStyle(QStyleFactory.create('dark_background'))
        self.MplWidget_tdoa.canvas.draw()

    def create_Nodes(self, position):
        node_positions = {}
        color_index = 0

        for uid in position:
            if uid == 'raw_position':
                continue
            if self._floor[uid]['nodeType'] == 'primary':
                node_positions[uid] = {'x': position[uid]['x']*1000, 'y': position[uid]['y']*1000, 'color': 'r', 'marker': 's' }
            else:
                node_positions[uid] = {'x': position[uid]['x']*1000, 'y': position[uid]['y']*1000, 'color': COLOR_PALET[color_index], 'marker': 'o' }
                color_index += 1
            
        for uid in self._floor:
            if uid not in position:
                node_positions[uid] = {'x': self._floor[uid]['x'], 'y': self._floor[uid]['y'], 'color': 'g', 'marker': 'o' }
        
        node_positions[TAG_ID] = {'x': position['raw_position']['x']*1000, 'y': position['raw_position']['y']*1000, 'color': 'b', 'marker': 'X'}
   
        return node_positions

    def create_hyperbola(self, position):
        
        tdoa = []
        node_position = []
        hyperbolas = {}
        color_index = 0

        for uid in position:
            if 'raw_position' in uid:
                continue
            if position[uid]['tdoa'] != 0.0:
                tdoa.append(position[uid]['tdoa'])
                node_position.append(np.array([position[uid]['x']*1000, position[uid]['y']*1000]))
                # add color to return value
                hyperbolas[uid] = { 'color': COLOR_PALET[color_index] }
                color_index += 1
            else:
                if len(tdoa) > 0:
                    tdoa.insert(0, position[uid]['tdoa'])
                    node_position.insert(0, np.array([position[uid]['x']*1000, position[uid]['y']*1000]))
                else:
                    tdoa.append(position[uid]['tdoa'])
                    node_position.insert(0, np.array([position[uid]['x']*1000, position[uid]['y']*1000]))

        locis = get_loci(np.array(tdoa), np.array(node_position), SPEED_OF_LIGHT, DELTA_D, MAX_D)
        
        if len(locis) != len(hyperbolas):
            return None

        for uid, loci in zip(hyperbolas, locis):
            hyperbolas[uid].update({'loci': loci})

        return hyperbolas

    def update_horizontal_slider(self, dict_length: int):
        self.horizontalSlider.maximum = dict_length-1
        self.horizontalSlider.setRange(0, dict_length-1)
        test = self.horizontalSlider.value()
        if self.horizontalSlider.value() == self.horizontalSlider.maximum-1:
            self.horizontalSlider.setValue(self.horizontalSlider.maximum)

    def on_tag_position(self, client: MQTTClient, userdata, message: MQTTMessage):
        global tag_position
        msg = json.loads(message.payload)
        tdoa_debug = {}

        if "tdoadebug" not in msg:
            return

        for tdoa in msg["tdoadebug"]:
            if 'raw_position' in tdoa:
                tdoa_debug.update(tdoa)
            else:
                tdoa_debug[tdoa.pop('uid')] = tdoa
        
        tag_position[msg["blink_count"]].update({ 'tdoadebug': tdoa_debug })
       
        self.update_horizontal_slider(len(tag_position))

    def on_tdoa(self, client: MQTTClient, userdata, msg: MQTTMessage, properties=None):

        try:
            node_uid = int(msg.topic.split("/")[1], 16)
        except:
            return
        messages = decoders[node_uid].decode(msg.payload)
        for message in messages:
            container = ReportContainer()
            container.node_id = node_uid

            if message.HasField("rtls_report_blink"):
                container.blink_report.CopyFrom(message.rtls_report_blink)
                if container.blink_report.tag_id == int(TAG_ID, base=16):

                    seq_nr = container.blink_report.sequence_number
                    tag_id = container.blink_report.tag_id

                    if seq_nr not in cache[tag_id]:
                        cache[tag_id][seq_nr] = BlinkCollection(
                            sequence_number=seq_nr, tag_id=tag_id, receive_time=int(time() * 1e6)
                        )
                    
                    cache[tag_id][seq_nr].blink_reports[container.node_id].CopyFrom(container)
                    
                    for tag_id, tag_blinks in cache.copy().items():
                        for seq_nr, blink_collection in tag_blinks.copy().items():
                            if int(time() * 1e6 - 50 * 10e3) > blink_collection.receive_time:
                                for report in blink_collection.blink_reports:
                                    blink_count = blink_collection.blink_reports[report].blink_report.blink.blink_count
                                    tag_position[blink_count].update({ 'blink_collection': cache[tag_id].pop(seq_nr) })
                                    break

        self.update_horizontal_slider(len(tag_position))

    def on_connect(self, client: MQTTClient, userdata, flags, rc):
        client.subscribe("tag/"+TAG_ID+"/position/"+str(FLOOR_ID))
        client.message_callback_add("tag/"+TAG_ID+"/position/"+str(FLOOR_ID), self.on_tag_position)

        client.subscribe("node/+/tdoa")
        client.message_callback_add("node/+/tdoa", self.on_tdoa)

class apiInterface:
    def __init__(self):

        self._floorlist = []
        self._apibase = API_BASE
        self._apitoken = API_TOKEN

        # to filter only the devicese that are currenctly used for twr
        self._node_filter_list = set(NODE_FILTER)
        pass

    def get_nodes(self):

        floors:Dict[Dict[Any]] = {}
        s:Session = Session()

        s.headers.update({"Authorization": "Api-Key {}".format(self._apitoken)})

        try:
            nodes_request = s.get(f"{self._apibase}/devices?type=node", timeout=HTTP_TIMEOUT)
        except RequestException as exc:
            logging.warning(f"Failed to get current Nodes: {exc}")
            sys.exit(1)

        if not nodes_request.ok:
            logging.warning(f"Failed to query API for Nodes: { nodes_request.reason }")
            sys.exit(1)

        if not nodes_request.json():
            logging.warning(f"No Nodes found")
            return {}

        for node in nodes_request.json():
            n = self.parse_props(node.get("properties", []))
            if not n:
                continue

            uid = n.pop('uid')

            if n is not None:
                if uid not in self._node_filter_list:
                    n["name"] = node["name"]
                    n["id"] = node["id"]
                    n['x'] = int(n['x'])
                    n['y'] = int(n['y'])
                    n['z'] = int(n['z'])

                    floor = int(n.pop("floor"))

                    if floor not in floors:
                        floors[floor] = {}
                    floors[floor][uid] = n
        
        self._floorlist = floors

        return floors

    def parse_props(self, props):

        n = {}

        for prop in props:
            if (
                prop["propId"]
                in [
                    NODE_UID_PROP_ID,
                    NODE_X_PROP_ID,
                    NODE_Y_PROP_ID,
                    NODE_Z_PROP_ID,
                    NODE_FLOOR_PROP_ID,
                    NODE_TYPE_PROP_ID
                ]
            ):
                if prop['name'] == 'floor' and prop['value'] is None:
                    return
                # if pos x and y are not existing just return
                elif (prop['name'] == 'x' or prop['name'] == 'y' or prop['name'] == 'z') and prop['value'] is None:
                    return
                else: 
                    n[prop["name"]] = prop["value"]

        return n

def nodes_from_list(name):

    f = open(name, 'r', newline='')
    reader = csv.reader(f, delimiter =',', dialect='excel')

    floors = {}

    # just a place holder for the second floor
    floor = 2

    for row in reader:
        if floor not in floors:
            floors[floor] = [{'uid' : row[0], 'name': row[1], 'x': float(row[2]), 'y': float(row[3]), 'z': float(row[4])}]
        else:
            floors[floor].append({'uid' : row[0], 'name': row[1], 'x': float(row[2]), 'y': float(row[3]), 'z': float(row[4])})

    return floors

if __name__ == "__main__":

    mqtt_client = MQTTClient()
    
    api = apiInterface()

    if API_ONLINE:
        floors = api.get_nodes()

    app = QApplication(sys.argv)
    window = Window(mqtt_client, TAG_ID, floors)
    window.show()
    app.exec_()
