from pymongo import MongoClient, ASCENDING, UpdateOne
from config import MONGO_URI, DB_NAME, MONGO_USER, MONGO_PASSWORD
from datetime import datetime

client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_URI}{DB_NAME}?authSource=admin')
db = client[DB_NAME]

message_collection = db["message"]
state_collection = db["backfill_state"]
channel = db["channel"]
sessions = db["sessions"]
worker_state = db["worker_state"]

def init_indexes():
    message_collection.create_index(
        [("hash", ASCENDING)],
        unique=True
    )

    state_collection.create_index(
        [("channel", ASCENDING)],
        unique=True
    )
    sessions.create_index(
        [("name", ASCENDING)],
        unique=True
    )
    sessions.create_index([("in_use", 1)])
    sessions.create_index([("worker_id", 1)])
    channel.create_index(
         [("name", ASCENDING)],
        unique=True
    ),


def save_signal(data):
    if "hash" not in data:
        raise ValueError("Missing hash")

    message_collection.update_one(
        {"hash": data["hash"]},  
        {"$set": data},
        upsert=True
    )
    print(f"message {data['message_id']} saved")

def save_session(name, api_id, api_hash, session_string, phone=None):
    sessions.update_one(
        {"name": name},
        {
            "$set": {
                "api_id": api_id,
                "api_hash": api_hash,
                "session_string": session_string,
                "phone": phone,
                "active": True,
                "updated_at": datetime.utcnow(),

                "in_use": False,
                "worker_id": None,
                "last_heartbeat": None
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    print(f"✅ Session {name} saved")


def bulk_save(data_list):
    operations = []

    for data in data_list:
        operations.append(
            UpdateOne(
                {"hash": data["hash"]},
                {"$set": data},
                upsert=True
            )
        )

    if operations:
        message_collection.bulk_write(operations, ordered=False)
        print(f"💾 Bulk saved {len(operations)} messages")