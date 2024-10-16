
import json
import base64
from datetime import datetime
import networkx as nx
from intranav.proto.inav_le_pb2 import GardenerReport

empty_on_line_tree = json.dumps(nx.node_link_data(nx.Graph())).encode("utf-8")

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

def compare(messages1, messages2):
    delta1 = 0
    delta2 = 0
    last_time1 = 0
    last_time2 = 0

    for message1, message2 in zip(messages1, messages2):
        currenten_time1 = message1["timestamp"]
        currenten_time2 = message2["timestamp"]

        if last_time1 != 0:
            delta1 = currenten_time1 - last_time1
        if last_time2 != 0:
            delta2 = currenten_time2 - last_time2
        
        last_time1 = currenten_time1
        last_time2 = currenten_time2
        print(delta1-delta2)


messages1 = load_splitter_data("splitter_data_2024-10-15_17-42-33.json")
messages2 = load_splitter_data("splitter_data_2024-10-15_17-43-05.json")

compare(messages1, messages2)