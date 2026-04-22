
import os
MONGO_URI = os.getenv("MONGO_URI")
MONGO_USER=  os.getenv("MONGO_USER")
MONGO_PASSWORD =  os.getenv("MONGO_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_NAME="test_telegram_db"

USE_PROXY= bool(os.getenv("USE_PROXY"))
PROXY = (
    "socks5",
    "host.docker.internal",
    10808,
) if USE_PROXY else None
CHANNELS = os.getenv("CHANNELS").split(",")
