import json

import networkx as nx

sync_file1 = "sync_data_2024-10-10_11-31-32.json"
sync_file2 = "sync_data_2024-10-10_11-46-43.json"


def load_sync_trees():
    seq_tree = {}
    with open(sync_file1, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            if data["tree_seq_nr"] not in seq_tree:
                seq_tree[data["tree_seq_nr"]] = {}
            seq_tree[data["tree_seq_nr"]]["tree1"] = nx.node_link_graph(json.loads(data["sync_tree"]))
    
    with open(sync_file2, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            if data["tree_seq_nr"] not in seq_tree:
                seq_tree[data["tree_seq_nr"]] = {}
            seq_tree[data["tree_seq_nr"]]["tree2"] = nx.node_link_graph(json.loads(data["sync_tree"]))

    return seq_tree

def remove_key(d, key):
    """Hilfsfunktion zum Entfernen eines Schlüssels aus einem Dictionary."""
    if key in d:
        del d[key]
    return d

def compare_trees(seqences):
    sequenced_diff_trees = {}
    for seq in seqences:
        if "tree1" not in seqences[seq]:
            print("kein tree1")
        elif "tree2" not in seqences[seq]:
            print("kein tree2")
        else:
            # 1. Knoten und deren Attribute vergleichen
            node_attr_diff = {}
            for node, attrs in seqences[seq]["tree1"].nodes(data=True):
                if node not in seqences[seq]["tree2"].nodes(data=True):
                    node_attr_diff[node[0]] = (seqences[seq]["tree1"].nodes[node[0]], seqences[seq]["tree2"].nodes.get(node[0], None))

            print("Unterschiedliche Knotenattribute:", node_attr_diff)

            edge_attr_diff = {}
            edge_diffs = {}
            
            for node1, node2, attrs in seqences[seq]["tree1"].edges(data=True):
                edge = (node1, node2)
                if edge in seqences[seq]["tree2"].edges:
                    G1_clean_attrs = remove_key(attrs.copy(), "update_kalman")
                    G2_clean_attrs = remove_key(seqences[seq]["tree2"].edges[edge].copy(), "update_kalman")

                    diff_attrs = {}
                    # Prüfe sowohl gemeinsame als auch nur in einem Graphen vorhandene Attribute
                    all_keys = set(G1_clean_attrs.keys()) | set(G2_clean_attrs.keys())

                    for k in all_keys:
                        G1_val = G1_clean_attrs.get(k, None)  # Falls Attribut in G1 fehlt, None
                        G2_val = G2_clean_attrs.get(k, None)  # Falls Attribut in G2 fehlt, None
                        if G1_val != G2_val:
                            diff_attrs[k] = (G1_val, G2_val)
                    
                    if diff_attrs:
                        edge_diffs[edge] = diff_attrs
                        if seq not in sequenced_diff_trees:
                            sequenced_diff_trees[seq] = nx.Graph()
                        sequenced_diff_trees[seq].add_node(node1)
                        sequenced_diff_trees[seq].add_node(node2)
                        sequenced_diff_trees[seq].add_edge(node1, node2, attr=edge_diffs[edge])
                        print(f"Für die ({node1:016x}, {node2:016x}) sequence: [{seq}], tree :{edge_diffs[edge]}")

if __name__ == "__main__":
    seqences = load_sync_trees()
    compare_trees(seqences)
