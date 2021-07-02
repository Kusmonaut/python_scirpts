"""
Intranav GmbH © 2021
check tag positioning
"""

from operator import sub
from numpy.testing._private.utils import measure
from scipy.integrate._ivp.radau import predict_factor
from sklearn import cluster
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
import statistics

from scipy.stats import gaussian_kde
from sklearn.neighbors import KernelDensity
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


measured_data = {}
tags = {}
typeOfInflexion = 'max'

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
                    if tdoa_message['uid'] in measured_data:
                        measured_data[tdoa_message['uid']].append(tdoa_message['tdoa'])
                    else:
                        measured_data[tdoa_message['uid']] = [tdoa_message['tdoa']]

# for uid in measured_data:
uid = '01aa2145caf203b4'
liste = []
for i, value in enumerate(measured_data[uid]):

    liste.append(value)

    data = np.array([liste]).T

    kde = KernelDensity(kernel='gaussian', bandwidth=5e-10).fit(data)

    if (i % 50) == 0:
        lw = 2
        X_plot = np.linspace(data.min()-3e-9, data.max()+3e-9, 1000)[:, np.newaxis]
        log_dens = kde.score_samples(X_plot)
        plt.plot(X_plot[:, 0], np.exp(log_dens), lw=lw,
                linestyle='-', label="kernel = 'gaussian'")
        test = X_plot[:,0]
        plt.show()
