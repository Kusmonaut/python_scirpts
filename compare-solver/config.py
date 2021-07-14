
import os


HTTP_TIMEOUT = 5.0
DELTA_D = 10                  # delta of the duty factor
MAX_D = 60                    # length of the hyperbula
SPEED_OF_LIGHT = 299702547     # speed of light in m/s
COLOR_PALET = ['#1f77b4', '#ff7f0e', '#5cb02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#23fe32', '#ffe325', '#0432fe', '#eb0043', '#f35d3f']
NODE_FILTER = {'01aa2145ca14452b', '01aa2145ca1440ad', '01aa2145ca144190', '01aa2145ca14458c', '01aa2145cae48a04', '01aa2145ca144288', '01aa2145ca141c2d', '01aa2145ca141bbb', '01aa2145ca141c94'}

# Grab configuration from environment variable
API_BASE = os.getenv('API_BASE', 'http://localhost:50080/api')
API_TOKEN = os.getenv('API_TOKEN',  'j14q5MPpftGBqS6vcTiPb1wIEDPImRBJ')
MILIMETER = int(os.getenv('MILIMETER',  1))
API_ONLINE = int(os.getenv('API_ONLINE',  1))
PLOT_ZONE = int(os.getenv('PLOT_ZONE',  0))
FILTER_TDOA = int(os.getenv('FILTER_TDOA',  1))
TDOA_REPORTS = os.getenv('TDOA_REPORTS', 'results/lufthansa24-04/asset_22_floor_2.json')
NODE_FROM_LIST = os.getenv('NODE_FROM_LIST', "./node_position/1_devices.csv")
MANUAL = int(os.getenv('MANUAL',  1))
X_MIN = int(os.getenv('X_MIN',  -5000))
X_MAX = int(os.getenv('X_MAX',  20000))
Y_MIN = int(os.getenv('Y_MIN',  4550))
Y_MAX = int(os.getenv('Y_MAX',  -10000))

if MILIMETER:
    DELTA_D = DELTA_D * 10
    MAX_D = MAX_D * 1000
    SPEED_OF_LIGHT = SPEED_OF_LIGHT * 1000 # mm/s