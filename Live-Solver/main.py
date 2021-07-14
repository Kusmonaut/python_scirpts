from paho.mqtt.client import Client as MQTTClient, MQTTMessage
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn.neighbors import KernelDensity
from matplotlib import style
import numpy as np
from scipy.ndimage.interpolation import shift
from scipy.signal import argrelextrema

MQTT_USER = "qt_services"
MQTT_PASS = "VXDY6KeqyTkJ5z8mqZm8"
MQTT_HOST = "192.168.1.99"
MQTT_PORT = 1883
RING_BUFFER_MOVEMENT = 10
RING_BUFFER_SLEEP = 100
RING_BUFFER_SLEEP = 100
BANDWIDTH = 2e-9
#BANDWIDTH = 6e-10
LINE_SPACE = 300
MIN_NUMBER_OF_TDOA_NODES = 3

TAGS = {}
# 10205f791000158c
TRACK_REF_NODE = '10205f791000158c'
TRACE_TAG = '05a260c907c40ca3'

def main():

    while True:

        if TRACE_TAG in TAGS:

            fig = plt.figure()

            def animate(i):
                lw = 2

                fig.clear()
                fig.suptitle(TRACK_REF_NODE)
                ax = []
                data = []
                kde = []

                #if TRACK_REF_NODE in TAGS[TRACE_TAG]:
                for i, tdoa_node in enumerate(TAGS[TRACE_TAG][TRACK_REF_NODE]):
                    test = [TAGS[TRACE_TAG][TRACK_REF_NODE][tdoa_node]]
                    data.append(np.array([TAGS[TRACE_TAG][TRACK_REF_NODE][tdoa_node]]).T)

                    kde.append(KernelDensity(kernel='gaussian', bandwidth=BANDWIDTH).fit(data[i]))
                
                    ax.append(fig.add_subplot(1,len(TAGS[TRACE_TAG][TRACK_REF_NODE]),i+1))

                    X_plot = np.linspace(data[i].min()-1e-8, data[i].max()+1e-8, 300)[:, np.newaxis]

                    log_dens = kde[i].score_samples(X_plot)

                    max = argrelextrema(log_dens, np.greater)[0]
                    min = argrelextrema(log_dens, np.less)[0]

                    # ax[i].clear()
                    
                    for m in max:
                        ax[i].axvline(X_plot[m])
                    
                    for m in min:
                        ax[i].axvline(X_plot[m])
                        
                    ax[i].plot(X_plot[:, 0], np.exp(log_dens), lw=lw,
                    linestyle='-', label="kernel = 'gaussian'")
                    # ax[i].xaxis.set_ticks(np.arange(data[i].min()-5e-9, data[i].max()+5e-9, 1e-9))
                    ax[i].set_title(tdoa_node)

            ani = animation.FuncAnimation(fig, animate, interval=100)

            plt.show()

def on_connect(client: MQTTClient, userdata, flags, rc):
    client.subscribe("tag/+/position/4")

def on_message(client: MQTTClient, userdata, message: MQTTMessage):
    global TAGS, TRACK_REF_NODE

    _ref_node_uid = ''
    _tag_id = ''

    position = json.loads(message.payload)

    # save tag_id
    _tag_id = position['id']

    if _tag_id not in TAGS:
        TAGS[_tag_id] = {}

    # # check tag is moved
    if position['tag_data']['state'] == 2:
        _ring_buffer_size = RING_BUFFER_MOVEMENT
        for ref_node in TAGS[_tag_id]:
            for node in TAGS[_tag_id][ref_node]:
                # cut dat till size of RING_BUFFER_MOVEMENT
                TAGS[_tag_id][ref_node][node] = TAGS[_tag_id][ref_node][node][(-RING_BUFFER_MOVEMENT):]

    else:
        _ring_buffer_size = RING_BUFFER_SLEEP

    # create refNode
    for debugNode in position['tdoadebug']:
        # create new RefNode
        if 'raw_position' not in debugNode:
            if debugNode['tdoa'] == 0:
                _ref_node_uid = debugNode['uid']
                if debugNode['uid'] not in TAGS[_tag_id]:
                    # create reference Node
                    TAGS[_tag_id][debugNode['uid']] = {}

                # TRACK_REF_NODE = _ref_node_uid
                break

    # add measuremnt to refnode
    for debugNode in position['tdoadebug']:


        if 'raw_position' not in debugNode:
            # get the node uid 
            node_uid = debugNode['uid']

            if debugNode['tdoa'] != 0:
                # check for the current tag if the the reference node has already this node in buffer
                if debugNode['uid'] not in TAGS[_tag_id][_ref_node_uid]:
                    TAGS[_tag_id][_ref_node_uid][debugNode['uid']] = []
                
                # if add or remove data from ringbuffer Size of RING_BUFFER
                if len(TAGS[_tag_id][_ref_node_uid][debugNode['uid']]) < _ring_buffer_size:
                    # save the measured tdoa data in buffer
                    TAGS[_tag_id][_ref_node_uid][debugNode['uid']].append(debugNode['tdoa'])
                else:
                    # add unfilterd data to the list
                    TAGS[_tag_id][_ref_node_uid][debugNode['uid']].pop(0)
                    TAGS[_tag_id][_ref_node_uid][debugNode['uid']].append(debugNode['tdoa'])

if __name__ == "__main__":

    mqtt_client = MQTTClient()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.loop_start()

    main()