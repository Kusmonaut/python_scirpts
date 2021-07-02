"""
IntraNav GmbH © 2021
Basic configuration for every service
"""
import os
import logging

from dotenv import load_dotenv

try:
    from version import __version__
except:
    __version__ = "develop"

# Load .env file if present
load_dotenv()

# Fixed Configurations
CHUNK_SIZE = 64
DECA_TIME_UNIT = 1.0 / 499.2e6 / 128.0  # in s
ENV = os.getenv("ENV", "prod")
HTTP_TIMEOUT = 5.0
LEGACY_CONFIG_TIME = 500.0  # Time to wait until config message is send to legacy tags
SERVICE_NAME = "cota"
SERVICE_VERSION = __version__
TIMEOUT_DEVICES = 10  # in s

# Grab configuration from environment variable
API_BASE = os.getenv("API_BASE", "http://backend:3000/api")
API_TOKEN = os.getenv("API_TOKEN", "j14q5MPpftGBqS6vcTiPb1wIEDPImRBJ")
MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.99")
MQTT_PASS = os.getenv("MQTT_PASS", "VXDY6KeqyTkJ5z8mqZm8")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "qt_services")
SENTRY_DSN = os.getenv(
    "SENTRY_DSN",
    "https://d129db0fdafd442487f9196b946ed0e6@o458391.ingest.sentry.io/5497449",
)
SENTRY_ENABLE = os.getenv("SENTRY_ENABLE", "false") in ["1", "t", "true", "y", "yes"]
SENTRY_LOCATION = os.getenv("SENTRY_LOCATION", "unknown")

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if ENV == "dev" else logging.INFO,
    format="%(asctime)s - %(name)s [%(levelname)s]: %(message)s",
)

if SENTRY_ENABLE and SENTRY_DSN and SERVICE_VERSION != "develop":
    import sentry_sdk

    sentry_sdk.init(
        SENTRY_DSN,
        traces_sample_rate=1.0,
        release=f"{SERVICE_NAME}@{SERVICE_VERSION}",
        integrations=[],
        environment=SENTRY_LOCATION,
    )