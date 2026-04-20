from pymongo import MongoClient, ASCENDING
from config import MONGO_URI, DB_NAME, MOGO_USER, MONGO_PASSWORD

client = MongoClient(f'mongodb://{MOGO_USER}:{MONGO_PASSWORD}@{MONGO_URI}{DB_NAME}')
db = client[DB_NAME]

signals_collection = db["signals"]
state_collection = db["backfill_state"]
channel = db["channel"]
sessions = db["sessions"]


def init_indexes():
    signals_collection.create_index(
        [("hash", ASCENDING)],
        unique=True
    )

    state_collection.create_index(
        [("channel", ASCENDING)],
        unique=True
    )

def save_signal(data):
    if "hash" not in data:
        raise ValueError("Missing hash")

    signals_collection.update_one(
        {"hash": data["hash"]},  
        {"$set": data},
        upsert=True
    )

    print(f"message {data['message_id']} saved")