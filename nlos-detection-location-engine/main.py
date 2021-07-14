"""
Intranav GmbH © 2021
nlos-detection-location-engine
"""

import json
import numpy as np

from sklearn.neighbors import KernelDensity
from scipy.signal import argrelextrema
from paho.mqtt.client import Client as MQTTClient, MQTTMessage

from average import *
from multilateration import *


MQTT_USER = "qt_services"
MQTT_PASS = "VXDY6KeqyTkJ5z8mqZm8"
MQTT_HOST = "192.168.1.99"
MQTT_PORT = 1883
RING_BUFFER_MOVEMENT = 10
RING_BUFFER_SLEEP = 100
BANDWIDTH = 2e-9
# BANDWIDTH = 8e-10
LINE_SPACE = 300
MIN_NUMBER_OF_TDOA_NODES = 3
FLOOR_ID = 8
CLE_FILTER_LENGTH=50

TAGS = {}


def on_connect(client: MQTTClient, userdata, flags, rc):
    client.subscribe("tag/+/position/4")

def on_message(client: MQTTClient, userdata, message: MQTTMessage):
    global TAGS

    _ref_node_uid = ''
    _tag_id = ''

    position = json.loads(message.payload)

    # save tag_id
    _tag_id = position['id']

    # add new tag to tag List and add also extendedAverage
    if _tag_id not in TAGS:
        TAGS[_tag_id] = { 'pos_filter': {}, 'ref_node': {} }
        TAGS[_tag_id]['pos_filter']['x_average'] = Average(CLE_FILTER_LENGTH)
        TAGS[_tag_id]['pos_filter']['y_average'] = Average(CLE_FILTER_LENGTH)
        TAGS[_tag_id]['pos_filter']['z_average'] = Average(CLE_FILTER_LENGTH)

    # # check tag is moved
    if position['tag_data']['state'] == 2:
        _ring_buffer_size = RING_BUFFER_MOVEMENT
        TAGS[_tag_id]['pos_filter']['x_average'].set_is_moving(True)
        TAGS[_tag_id]['pos_filter']['y_average'].set_is_moving(True)
        TAGS[_tag_id]['pos_filter']['z_average'].set_is_moving(True)

        for ref_node in TAGS[_tag_id]['ref_node']:
            for node in TAGS[_tag_id]['ref_node'][ref_node]:
                # cut dat till size of RING_BUFFER_MOVEMENT
                TAGS[_tag_id]['ref_node'][ref_node][node] = TAGS[_tag_id]['ref_node'][ref_node][node][(-RING_BUFFER_MOVEMENT):]

    else:
        _ring_buffer_size = RING_BUFFER_SLEEP
        TAGS[_tag_id]['pos_filter']['x_average'].set_is_moving(False)
        TAGS[_tag_id]['pos_filter']['y_average'].set_is_moving(False)
        TAGS[_tag_id]['pos_filter']['z_average'].set_is_moving(False)

    # create refNode
    for debugNode in position['tdoadebug']:
        # create new RefNode
        if 'raw_position' not in debugNode:
            if debugNode['tdoa'] == 0:
                _ref_node_uid = debugNode['uid']
                if debugNode['uid'] not in TAGS[_tag_id]['ref_node']:
                    # create reference Node
                    TAGS[_tag_id]['ref_node'][debugNode['uid']] = {}
                break

    # add measuremnt to refnode
    for debugNode in position['tdoadebug']:

        if 'raw_position' not in debugNode:
            # get the node uid 
            node_uid = debugNode['uid']

            if debugNode['tdoa'] != 0:
                # check for the current tag if the the reference node has already this node in buffer
                if node_uid not in TAGS[_tag_id]['ref_node'][_ref_node_uid]:
                    TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid] = []
                
                # if add or remove data from ringbuffer Size of RING_BUFFER
                if len(TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid]) < _ring_buffer_size:
                    # save the measured tdoa data in buffer
                    TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid].append(debugNode['tdoa'])

                    # filter wrong tdoa measurement
                    debugNode['tdoa'] = filter_or_correcting_positioningNodes(TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid], debugNode['tdoa'])
                else:
                    # add unfilterd data to the list
                    TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid].pop(0)
                    TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid].append(debugNode['tdoa'])

                    # filter wrong tdoa measurement
                    debugNode['tdoa'] = filter_or_correcting_positioningNodes(TAGS[_tag_id]['ref_node'][_ref_node_uid][node_uid], debugNode['tdoa'])

    # change Floor id in message
    position['floorId'] = FLOOR_ID
    
    if len(position['tdoadebug']) >= MIN_NUMBER_OF_TDOA_NODES:
        # calc new positi on
        _calc_pos = calc_tag_position(position['tdoadebug'])
 
        if np.shape(_calc_pos) == (1, 3):
            position['pos']['x'] = Motion_Filter_ME( TAGS[_tag_id]['pos_filter']['x_average'], _calc_pos[0][0] )
            position['pos']['y'] = Motion_Filter_ME( TAGS[_tag_id]['pos_filter']['y_average'], _calc_pos[0][1] )

            # publish new position 
            _topic = 'tag/' + position['id'] + '/position/' + str(FLOOR_ID)
            _payload = json.dumps(position)
            client.publish(_topic, _payload)

def calc_tag_position(tdoa_debug):

    _tdoa = []
    _node_pos = []
    multilaterator = MultiLateration()
    cleSolver3D = False

    for node in tdoa_debug:
        if 'raw_position' not in node:
            _tdoa.append(node['tdoa'])
            _node_pos.append((node['x'], node['y']))

    multilaterator.setNodes(np.mat(_node_pos), cleSolver3D)
    _calc_result = multilaterator.multilaterate(np.array([_tdoa]), cleSolver3D)

    return _calc_result

def filter_or_correcting_positioningNodes(dataset, tdoa):
    
    _local_maxima = 0
    _local_minima = 0
    _cluster_sets = []

    if len(dataset) <= 1:
        return tdoa

    _data = np.array([dataset]).T

    # create instance of the kernel density estimation
    _kde = KernelDensity(kernel='gaussian', bandwidth=BANDWIDTH).fit(_data)

    # define the line range of the kde by using the min and max of the _data
    _x_plot = np.linspace(_data.min()-1e-8, _data.max()+1e-8, LINE_SPACE)[:, np.newaxis]
    
    _log_dens = _kde.score_samples(_x_plot)
    
    # get all minima and maxima from the kde graph
    _local_maxima = argrelextrema(_log_dens, np.greater)[0]
    _local_minima = argrelextrema(_log_dens, np.less)[0]

    # change the order of the modes from highest to lowest modes
    _anti_modes = _x_plot[np.sort(_local_minima)[::-1]]
    _modes = _x_plot[np.sort(_local_maxima)[::-1]]

    # create sub clusters with the found anti modes
    if len(_anti_modes) > 0:
        for splitter in _anti_modes:
            _dataset_index = _data > splitter
            _cluster_sets.append(_data[_dataset_index])
            _data = _data[np.invert(_dataset_index)]

        _dataset_index = _data <= _x_plot[_local_minima[0]]
        _cluster_sets.append(_data[_dataset_index])

        # filter the tdoa measurement
        tdoa = find_cluster(_modes, _cluster_sets, tdoa)

    return tdoa


def find_cluster(modes, cluster_sets, tdoa):
    # check that clusters exist
    if len(modes) > 0 and len(cluster_sets) > 0:
        
        # calc standard deviation of the first cluster
        stdeviation = np.std(cluster_sets[0])

        # check if the tdoa measurement is in the 5th standard deviation
        if (stdeviation * 5) + modes[0] > tdoa and tdoa > (stdeviation * -5) + modes[0]:

            # if there are more modes go one instance deeper and retry
            if len(modes[1:]) > 0 and len(cluster_sets[1:]) > 0:

                # shift the tdoa value to the second cluster
                tdoa2 = tdoa - (modes[0][0] - modes[1][0])

                tdoa2 = find_cluster( modes=modes[1:], cluster_sets=cluster_sets[1:], tdoa=tdoa2 )
                if tdoa2 != None:
                    return tdoa2
                else:
                    return tdoa
            else:
                return tdoa
        else:
            if len(modes[1:]) > 0 and len(cluster_sets[1:]) > 0:
                return find_cluster( modes=modes[1:], cluster_sets=cluster_sets[1:], tdoa=tdoa )
            else:
                return None
    return tdoa

def main():
    pass

if __name__ == "__main__":
    mqtt_client = MQTTClient()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.loop_forever()

    main()
