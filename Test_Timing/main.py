import time
import json
import base64
from datetime import datetime
from queue import Queue

import networkx as nx
from intranav.proto.inav_le_pb2 import GardenerReport

expire_queue= Queue()
empty_on_line_tree = json.dumps(nx.node_link_data(nx.Graph())).encode("utf-8")
graph_seq = -1
filename_track_recording = datetime.now().strftime("splitter_data_%Y-%m-%d_%H-%M-%S.json")
sync_tree_gardener = None



def save_splitter_data(payload, node_uid, sync_tree_gardener):
    global graph_seq
    data = {}
    data["timestamp"] = time.time()
    data["node_uid"] = node_uid
    data["payload"] = base64.b64encode(payload).decode('utf-8')
    if sync_tree_gardener:
        if sync_tree_gardener.graph["seq_nr"] != graph_seq:
            if "sync_tree_gardener" not in data:
                data["sync_tree_gardener"] = {}
            data["sync_tree_gardener"] =  json.dumps(nx.node_link_data(sync_tree_gardener))
            graph_seq = sync_tree_gardener.graph["seq_nr"]
        # json.dumps(nx.node_link_data(sync_tree_gardener))
    with open(filename_track_recording, 'a') as f:
        f.write(json.dumps(data) + "\n")

def load_splitter_data(filename):
    messages = []
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            node_uid = data["node_uid"]
            payload = base64.b64decode(data["payload"])
            current_timestamp = data["timestamp"]
            message = {"node_uid": node_uid, "payload": payload, "timestamp": current_timestamp}
            if "sync_tree_gardener" in data:
                sync_tree_gardener = nx.node_link_graph(json.loads(data["sync_tree_gardener"]))
                gardener_message = GardenerReport()
                binary_sync_tree = json.dumps(nx.node_link_data(sync_tree_gardener)).encode("utf-8")
                gardener_message.on_line_tree = empty_on_line_tree
                gardener_message.sync_tree = binary_sync_tree
                message["gardener_message"] = gardener_message
                message["sync_tree_gardener"] = sync_tree_gardener
            messages.append(message)
    return messages

def create_test_file():

    current_time = time.time()
    node_uid = 0

    current_time = int(current_time)
    payload = b"234234dfsadr234"
    for i in range(100000):
        data = {}
        data["timestamp"] = current_time + i * 0.001
        data["node_uid"] = node_uid + i
        data["payload"] = base64.b64encode(payload).decode('utf-8')
        with open(filename_track_recording, 'a') as f:
            f.write(json.dumps(data) + "\n")

filename = "splitter_data_2024-10-17_15-21-35.json"
messages = load_splitter_data(filename)

delta = 0
start_time = 0.0
save_for_print = []
current_time = time.time()

for data in messages:
    if delta == 0:
        delta = (current_time + 3) - data["timestamp"]
    intervall = data["timestamp"] + delta
    expire_queue.put((data, intervall))   
    

while not expire_queue.empty():

    data, intervall = expire_queue.get()

    while intervall > time.time():
        pass
    save_splitter_data(data["payload"], data["node_uid"], sync_tree_gardener)
    if start_time == 0.0:
        start_time = time.time()
    time_d = time.time() - start_time
    node_id = data["node_uid"]
    save_for_print.append((node_id, time_d))

for node_id, time_d in save_for_print:
    print(f"{node_id} \t, {time_d:.6f}")