
from tkinter import *
from paho.mqtt.client import Client as MqttClient, MQTTMessage
import json
import os
import time
from dotenv import load_dotenv


# Load .env file if present
load_dotenv()
mqtt_client = MqttClient()

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.99")
MQTT_PASS = os.getenv("MQTT_PASS", "VXDY6KeqyTkJ5z8mqZm8")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "qt_services")

def message1(event):

    
    topic = "node/" + "01aa2145ca141c2d" + "/cmd"
    mqtt_client.publish(topic, payload='{"cmd": "twr_responder", "initiator": "01aa2145cae4848e", "responder": "01aa2145ca141c2d"}')
    
    time.sleep(0.1)

    topic = "node/" + "01aa2145cae4848e" + "/cmd"
    mqtt_client.publish(topic, payload='{"cmd": "twr_initiator", "initiator": "01aa2145cae4848e", "responder": "01aa2145ca141c2d", "num_twr_ranges":'+ entry1.get() + '}')


def message2(event):

    
    topic = "node/" + "01aa2145cae4848e" + "/cmd"
    mqtt_client.publish(topic, payload='{"cmd": "twr_responder", "initiator": "01aa2145ca141c2d", "responder": "01aa2145cae4848e" }')

    time.sleep(0.1)

    topic = "node/" + "01aa2145ca141c2d" + "/cmd"
    mqtt_client.publish(topic, payload='{"cmd": "twr_initiator", "initiator": "01aa2145ca141c2d", "responder": "01aa2145cae4848e", "num_twr_ranges":' + entry2.get() + '}')
    

if __name__ == "__main__":
    data = []
    with open('mqtt_commands.json') as f:
        data = json.load(f)

    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

    mqtt_client.connect(MQTT_HOST, port=MQTT_PORT)
    mqtt_client.loop_start()

    root = Tk()
    root.geometry("450x100")

    button1 = Button(root ,text="141c2d <-> e48a04")
    button2 = Button(root ,text="e48a04 <-> 141c2d")

    entry1 = Entry(root)
    entry2 = Entry(root)

    button1.pack()
    button2.pack()

    ## layout
    button1.place(x=25, y=25)
    button2.place(x=275, y=25)

    entry1.place(x=25, y=55)
    entry2.place(x=275, y=55)

    button1.bind("<Button-1>", message1)
    button2.bind("<Button-1>", message2)

    root.mainloop()