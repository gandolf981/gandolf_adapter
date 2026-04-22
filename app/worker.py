
from datetime import datetime
import socket
from db import sessions
import time 

WORKER_ID = socket.gethostname()  # or uuid


def acquire_session():
    session = sessions.find_one_and_update(
        {
            "in_use": False
        },
        {
            "$set": {
                "in_use": True,
                "worker_id": WORKER_ID,
                "last_heartbeat": datetime.utcnow()
            }
        },
        sort=[("last_heartbeat", 1)],  # optional fairness
        return_document=True
    )
    print("*"*80)
    print(session)
    return session

def release_session(session_name):
    sessions.update_one(
        {"name": session_name},
        {
            "$set": {
                "in_use": False,
                "worker_id": None
            }
        }
    )

def heartbeat(session_name):
    while True:
        sessions.update_one(
            {"name": session_name},
            {
                "$set": {
                    "last_heartbeat": datetime.utcnow()
                }
            }
        )
        time.sleep(10)

from datetime import timedelta

def release_stale_sessions():
    timeout = datetime.utcnow() - timedelta(seconds=30)

    sessions.update_many(
        {
            "in_use": True,
            "last_heartbeat": {"$lt": timeout}
        },
        {
            "$set": {
                "in_use": False,
                "worker_id": None
            }
        }
    )