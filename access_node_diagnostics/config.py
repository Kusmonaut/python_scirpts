"""
INTRANAV Location Engine v2 Config
"""
from dotenv import load_dotenv
from os import getenv
import numpy

try:
    from version import __version__  # type: ignore
except:
    __version__ = "develop"

# Load .env file if present
load_dotenv()

# Constant Configurations
SERVICE_NAME = "location-engine"
SERVICE_VERSION = __version__
# Decawave Specific Constants
DECA_TIME_UNIT = numpy.longdouble(1000.0 / 499.2e6 / 128.0)  # in ms
CLOCK_PERIOD = numpy.longdouble(0x10000000000)
CLOCK_PERIOD_MILI_SEC = numpy.longdouble(CLOCK_PERIOD * DECA_TIME_UNIT)
CLOCK_HALF_PERIOD_MILI_SEC = numpy.longdouble(CLOCK_PERIOD_MILI_SEC / 2.0)
C_MILI_METER_PER_MILI_SECONDS	= 299702547.0				#Speed of Light mm/ms

# Configuration
ENV = getenv("ENV", "prod")
MQTT_HOST = getenv("MQTT_HOST", "192.168.1.99")
MQTT_PASS = getenv("MQTT_PASS", "VXDY6KeqyTkJ5z8mqZm8")
MQTT_PORT = int(getenv("MQTT_PORT", "1883"))
MQTT_USER = getenv("MQTT_USER", "qt_services")

FRAME_HEADER_LEN = 6
STX = 0x02
ETX = 0x03
ACC_HEAD = 15
ACC_DATA = 20
ACC_LOG = 4055
ACCESS_ACCUMULATOR_MEMORY = {"cmd":"record_acc"}
FRAME_DATA_IDX = 3
RTLS_LOG_ACCUMULATOR_IND = 0x91         # DEC 145
RTLS_DW_ACCUMULATOR_LEN_16 = (992*4+1)  # 6M PRF is 992*4+1
RTLS_DW_ACCUMULATOR_LEN_64 = (1016*4+1) # 64M PRF is 1016*4+1