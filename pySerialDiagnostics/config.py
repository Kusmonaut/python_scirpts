
import os


HTTP_TIMEOUT = 5.0
DELTA_D = 100                   # delta of the duty factor
MAX_D = 60000                     # length of the hyperbula in mm
SPEED_OF_LIGHT = 299702547000     # speed of light in mm/s
COLOR_PALET = ['#1f77b4', '#ff7f0e', '#5cb02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#23fe32', '#ffe325', '#0432fe', '#eb0043', '#f35d3f']
NODE_FILTER = {'01aa2145ca14452b'}

# Grab configuration from environment variable
MQTT_USER =  os.getenv('MQTT_USER', 'qt_services')
MQTT_PASS =  os.getenv('MQTT_PASS', 'VXDY6KeqyTkJ5z8mqZm8')
MQTT_HOST =  os.getenv('MQTT_HOST', '192.168.1.99')
MQTT_PORT =  int(os.getenv('MQTT_PORT', 1883))
API_BASE = os.getenv('API_BASE', 'http://192.168.1.99/api')
API_TOKEN = os.getenv('API_TOKEN',  'j14q5MPpftGBqS6vcTiPb1wIEDPImRBJ')
API_ONLINE = int(os.getenv('API_ONLINE',  1))
MANUAL = int(os.getenv('MANUAL',  1))   # manual setting of the plot window size 
X_MIN = int(os.getenv('X_MIN',  -2870))
X_MAX = int(os.getenv('X_MAX',  6370))
Y_MIN = int(os.getenv('Y_MIN', 9400))
Y_MAX = int(os.getenv('Y_MAX',  16050))
PHYSICAL_TAG_POSITION_X =int(os.getenv('PHYSICAL_TAG_POSITION_X', 4520))
PHYSICAL_TAG_POSITION_Y = int(os.getenv('PHYSICAL_TAG_POSITION_Y',  9940)) 
FLOOR_ID = int(os.getenv('FLOOR_ID', 8))
TAG_ID =  os.getenv('TAG_ID', "05a260c947c41299")
SOLVER_MIN_NUMBER_REPORTS = 3