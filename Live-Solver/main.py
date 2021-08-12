
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from paho.mqtt.client import Client as MQTTClient, MQTTMessage
from sklearn.neighbors import KernelDensity
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
TRACE_TAG = '05a260c907c40a14'

TAGS = {}

def main():

    while True:

        if TRACE_TAG in TAGS:

            fig = plt.figure()

            def animate(i):

                fig.clear()
                columns = []
                ax = []
                data = []
                kde = []
                lw = 2

                # list sizes of columns
                for tdoa_node in TAGS[TRACE_TAG]:
                    columns.append(len(TAGS[TRACE_TAG][tdoa_node]))
                
                # get the size max row and max column
                max_row_size = len(TAGS[TRACE_TAG])
                max_column_size = max(columns)
                
                for i, ref_node in enumerate(TAGS[TRACE_TAG]):
                    ax.append([])
                    data.append([])
                    kde.append([])

                    for j, tdoa_node in enumerate(TAGS[TRACE_TAG][ref_node]):

                        data[i].append(np.array([TAGS[TRACE_TAG][ref_node][tdoa_node]]).T)
                        
                        kde[i].append(KernelDensity(kernel='gaussian', bandwidth=BANDWIDTH).fit(data[i][j]))

                        X_plot = np.linspace(data[i][j].min()-1e-8, data[i][j].max()+1e-8, 300)[:, np.newaxis]
                        
                        log_dens = kde[i][j].score_samples(X_plot)

                        max_mode = argrelextrema(log_dens, np.greater)[0]
                        min_mode = argrelextrema(log_dens, np.less)[0]
                        
                        ax[i].append(plt.subplot2grid(shape=(max_row_size, max_column_size), loc=(i,j), title=tdoa_node) )

                        for m in max_mode:
                            ax[i][j].axvline(X_plot[m])
                        
                        for m in min_mode:
                            ax[i][j].axvline(X_plot[m])

                        ax[i][j].plot(X_plot[:, 0], np.exp(log_dens), lw=lw, linestyle='-', label="kernel = 'gaussian'")

                        ax[i][j].set_title(tdoa_node)

            ani = animation.FuncAnimation(fig, animate, interval=100)

            plt.show()

def on_connect(client: MQTTClient, userdata, flags, rc):
    client.subscribe("tag/+/position/4")

def on_message(client: MQTTClient, userdata, message: MQTTMessage):
    global TAGS

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