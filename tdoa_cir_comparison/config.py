
import os


HTTP_TIMEOUT = 5.0
DELTA_D = 100                   # delta of the duty factor
MAX_D = 60000                     # length of the hyperbula in mm
SPEED_OF_LIGHT = 299702547000     # speed of light in mm/s
COLOR_PALET = ['#1f77b4', '#ff7f0e', '#5cb02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#23fe32', '#ffe325', '#0432fe', '#eb0043', '#f35d3f']
NODE_FILTER = {'01aa2145ca14452b', '01aa2145ca1440ad', '01aa2145ca144190', '01aa2145ca14458c', '01aa2145cae48a04', '01aa2145ca144288', '01aa2145ca141c2d', '01aa2145ca141bbb', '01aa2145ca141c94'}

# Grab configuration from environment variable
API_BASE = os.getenv('API_BASE', 'http://192.168.1.99:80/api')
API_TOKEN = os.getenv('API_TOKEN',  'j14q5MPpftGBqS6vcTiPb1wIEDPImRBJ')
API_ONLINE = int(os.getenv('API_ONLINE',  1))
TDOA_REPORTS = os.getenv('TDOA_REPORTS', 'results/1633077610/asset_92_floor_4.json')
NODE_FROM_LIST = os.getenv('NODE_FROM_LIST', "./node_position/1_devices.csv")
MANUAL = int(os.getenv('MANUAL',  1))   # manual setting of the plot window size 
X_MIN = int(os.getenv('X_MIN',  -11780))
X_MAX = int(os.getenv('X_MAX',  74150))
Y_MIN = int(os.getenv('Y_MIN', 10550))
Y_MAX = int(os.getenv('Y_MAX',  -36630))