"""
Intranav GmbH © 2021
check tag positioning
"""

from scipy.integrate._ivp.radau import predict_factor
from yellowbrick.utils.kneed import KneeLocator
from config import logging
from scipy.stats import norm
import json
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import kneed

from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer, KElbow
from yellowbrick.cluster.elbow import kelbow_visualizer
from sklearn.metrics import silhouette_samples, silhouette_score, calinski_harabasz_score, davies_bouldin_score


TDOA_REPORTS = os.getenv('TDOA_REPORTS', 'results/lufthansa24-04/asset_22_floor_2.json')
MILIMETER = int(os.getenv('MILIMETER',  1))

from config import (
    API_BASE,
    API_TOKEN,
    HTTP_TIMEOUT,
    MQTT_HOST,
    MQTT_PASS,
    MQTT_PORT,
    MQTT_USER,
)

messured_data = {}
tags = {}

try:
    f = open(TDOA_REPORTS)
    data = json.load(f)
except OSError as exc:
    logging.warning(f"Failed to open file: {exc}")
    sys.exit(1)

for entrence in data:
    if entrence['asset']['assetId'] is not None:
        uid = entrence['asset']['assetId']
    else:
        # if asset/ assetId doesnt exist save tag with uid
        uid = entrence.pop('id')

    # change the units from meter to millimeter
    if MILIMETER:
        entrence['pos']['x'] = int(entrence['pos']['x']*1000)
        entrence['pos']['y'] = int(entrence['pos']['y']*1000)
        try:
            for node in entrence['tdoadebug']:
                node['x'] = int(node['x']*1000)
                node['y'] = int(node['y']*1000)
                node['z'] = int(node['z']*1000)
        except:
            pass

    if uid not in tags:
        tags[uid] = [entrence]
    else:
        tags[uid].append(entrence)

for uid in tags: 
    tags[uid] = sorted(tags[uid], key=lambda k: k['time']) 

for uid in tags:
    for entrence in tags[uid]:
        if [sub['tdoa'] == 0.0 and sub['uid'] == '01aa2145cae48b16' for sub in entrence['tdoadebug']]:
            for tdoa_message in entrence['tdoadebug']:
                if tdoa_message['tdoa'] != 0:
                    if tdoa_message['uid'] in messured_data:
                        messured_data[tdoa_message['uid']].append(tdoa_message['tdoa'])
                    else:
                        messured_data[tdoa_message['uid']] = [tdoa_message['tdoa']]



score = {}

for uid in messured_data:

    data = np.array([messured_data[uid]]).T

    if uid == '01aa2145caf203b4':
        for value in messured_data[uid]:
            if value < 0:
                messured_data[uid].remove(value)
                # -5.8408445191560077e-08
                # 1.1850900483167948e-08
    
    score.update({ uid: [] })
    km = []
    
    # kreate k-means and locate elbows
    for i,k in enumerate([1,2,3,4,5]):
        km.append(KMeans(n_clusters=k))
        km[i].fit(data)
        score[uid].append({'cluster_error':km[i].inertia_, 'cluster_num': k})

    cluster_num = [value['cluster_num'] for value in score[uid]]
    cluster_error = [value['cluster_error'] for value in score[uid]]
    location = KneeLocator(cluster_num, cluster_error, S=1.83, curve_nature='convex', curve_direction='decreasing')

    # check if k-means has multiple clusters
    if location.knee:
        cluster_id = km[location.elbow-1].predict(data)

        fig, ax = plt.subplots()
        bins = np.linspace(data.min(), data.max(), 50)

        for ii in np.unique(cluster_id):
            subset = data[cluster_id==ii]
            ax.hist(subset, bins= 1000, alpha=0.5, label=f"Cluster {ii}")
        ax.legend()
        plt.show()
        
        plt.axvline(x=location.knee, linestyle='-.', color='k')

    plt.plot(cluster_num, cluster_error)
    plt.show()
