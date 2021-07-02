from paho.mqtt.client import Client as MQTTClient, MQTTMessage
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn.neighbors import KernelDensity
from matplotlib import style
import numpy as np

MQTT_USER = "qt_services"
MQTT_PASS = "VXDY6KeqyTkJ5z8mqZm8"
MQTT_HOST = "192.168.1.99"
MQTT_PORT = 1883

REF_NODE = {}
TRACK_REF_NODE = '01aa2145ca144239'



def main():
    
    while True:
        if TRACK_REF_NODE in REF_NODE:
            ax = []
            
            fig = plt.figure()

            for i, tdoa_node in enumerate(REF_NODE[TRACK_REF_NODE]):
            
                if len(REF_NODE[TRACK_REF_NODE][tdoa_node]) > 10:
                    data = np.array([REF_NODE[TRACK_REF_NODE][tdoa_node]]).T
                    kde = KernelDensity(kernel='gaussian', bandwidth=5e-10).fit(data)
                
                    ax.append(fig.add_subplot(2,len(REF_NODE[TRACK_REF_NODE]),i))

            def animate(i):
                lw = 2
                X_plot = np.linspace(data.min()-3e-9, data.max()+3e-9, 1000)[:, np.newaxis]
                log_dens = kde.score_samples(X_plot)
                ax[i].clear()
                ax[i].plot(X_plot[:, 0], np.exp(log_dens), lw=lw,
                linestyle='-', label="kernel = 'gaussian'")

            ani = animation.FuncAnimation(fig, animate, interval=1000)
            plt.show()

def on_connect(client: MQTTClient, userdata, flags, rc):
    client.subscribe("tag/05a260c907c40ca3/position/3")

def on_message(client: MQTTClient, userdata, message: MQTTMessage):
    global REF_NODE

    local_ref = ''

    position = json.loads(message.payload)
    
    # create refNode
    for debugNode in position['tdoadebug']:
        # create new RefNode
        if 'raw_position' not in debugNode:
            if debugNode['tdoa'] == 0:
                local_ref = debugNode['uid']
                if debugNode['uid'] not in REF_NODE:
                    REF_NODE[debugNode['uid']] = {}

    # add measuremnt to refnode
    for debugNode in position['tdoadebug']:

        if 'raw_position' not in debugNode:
            if debugNode['tdoa'] != 0:
                if debugNode['uid'] not in REF_NODE[local_ref]:
                    REF_NODE[local_ref][debugNode['uid']] = [debugNode['tdoa']]
                else:
                    REF_NODE[local_ref][debugNode['uid']].append(debugNode['tdoa'])

if __name__ == "__main__":

    mqtt_client = MQTTClient()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.loop_start()

    main()