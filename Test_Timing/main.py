import time
import threading
import json
import base64
from datetime import datetime

import networkx as nx
from intranav.proto.inav_le_pb2 import GardenerReport

empty_on_line_tree = json.dumps(nx.node_link_data(nx.Graph())).encode("utf-8")
graph_seq = -1
filename_track_recording = datetime.now().strftime("splitter_data_%Y-%m-%d_%H-%M-%S.json")
sync_tree_gardener = None

class MultiTTLCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
    
    def set(self, key, value, ttl):
        """Fügt einen Eintrag mit einer individuellen TTL basierend auf `time.monotonic()` hinzu."""
        expiration_time = time.perf_counter() + ttl
        with self.lock:
            self.cache[key] = (value, expiration_time)
        print(f"Daten in Cache eingefügt: {key}, TTL: {ttl} Sekunden")
    
    def get_expired_entries(self):
        """Gibt eine Liste der abgelaufenen Einträge zurück und entfernt sie."""
        with self.lock:
            expired_keys = [(key, (value, expiration_time)) for key, (value, expiration_time) in self.cache.items() if time.perf_counter() >= expiration_time]
            for key in expired_keys:
                del self.cache[key[0]]
        return expired_keys

# Beispiel-Funktion, die die Daten verarbeitet
def sende_daten(daten):
    print(f"Daten gesendet: {daten}")

# Consumer-Thread, der die abgelaufenen Daten verarbeitet
def consumer(cache):
    global sync_tree_gardener
    while True:
        expired_entries = cache.get_expired_entries()
        for key, values in expired_entries:
            if "sync_tree_gardener" in values[0]:
                sync_tree_gardener = values["sync_tree_gardener"]
            # sende_daten(key)
            save_splitter_data(values[0]['payload'], values[0]['node_uid'], sync_tree_gardener)

        time_to_sleep = 0.0001  # Standard-Schlafzeit, wenn kein Eintrag im Cache ist
        # Schlafe bis zum nächsten Ablauf
        time.sleep(time_to_sleep)

timestamp_set = {}
# Producer-Thread, der mehrere Daten mit unterschiedlichen TTLs in den Cache einfügt
def producer(cache):

    filename = "splitter_data_2024-10-15_17-42-33.json"
    messages = load_splitter_data(filename)
    ttl = 0
    start_time = 0
    
    for daten in messages:
        if start_time == 0:
            start_time = daten["timestamp"]
        else:
            ttl = daten["timestamp"] - start_time
        key = daten["timestamp"]
        cache.set(key, daten, ttl)  # Füge mehrere Daten mit TTL in den Cache ein
        timestamp_set[key] = time.perf_counter()
        time.sleep(0.0003)  # Simuliere eine Verzögerung zwischen den Einfügungen


def save_splitter_data(payload, node_uid, sync_tree_gardener):
    global graph_seq
    data = {}
    data["timestamp"] = time.perf_counter()
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


# Cache erstellen
cache = MultiTTLCache()

# Starten der Threads
consumer_thread = threading.Thread(target=consumer, args=(cache,))
producer_thread = threading.Thread(target=producer, args=(cache,))

# Threads als Daemon setzen, damit sie beendet werden, wenn das Hauptprogramm endet
consumer_thread.daemon = True
producer_thread.daemon = True

# Threads starten
producer_thread.start()
consumer_thread.start()

# Warten, bis der Producer fertig ist
producer_thread.join()

print("Alle Daten wurden in den Cache eingefügt und verarbeitet.")
while True:
    pass