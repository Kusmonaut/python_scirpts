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
TDOA_REPORTS_FILTER = os.getenv('TDOA_REPORTS', 'results/lufthansa24-04/asset_22_floor_2_corrected.json')
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

try:
    f_r = open(TDOA_REPORTS)
    f_w = open(TDOA_REPORTS_FILTER, 'w')
    data = json.load(f_r)
except OSError as exc:
    logging.warning(f"Failed to open file: {exc}")
    sys.exit(1)

for entrence in data:
    if [tdoa['uid'] == '01aa2145caf20e92' and tdoa['tdoa'] == 0 for tdoa in entrence['tdoadebug']]:
        for i, tdoa in enumerate(entrence['tdoadebug']):
            if tdoa['uid'] == '01aa2145caf203b4' and tdoa['tdoa'] > 1e-8:
                entrence['tdoadebug'][i]['tdoa'] = entrence['tdoadebug'][i]['tdoa'] - 5.1e-9

json.dump(data, f_w)

f_w.close()