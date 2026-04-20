
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
# API_ID="33191010"
# API_HASH="e85c932b610556f5f76579b45e31b47b"
MONGO_URI = os.getenv("MONGO_URI")
MOGO_USER=  os.getenv("MONGO_USER")
MONGO_PASSWORD =  os.getenv("MONGO_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

CHANNELS = os.getenv("CHANNELS").split(",")
# CHANNELS = "VASILY_TRADER_FOREX_SIGNALS"

PROXY = (
    "socks5",
    "host.docker.internal",
    10808,
)
