from datetime import datetime, timezone
from db import worker_state


def update_state(worker_id, data):
    worker_state.update_one(
        {"worker_id": worker_id},
        {
            "$set": {
                **data,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )


def get_state(worker_id=None):
    if worker_id:
        return worker_state.find_one({"worker_id": worker_id}, {"_id": 0})
    
    return list(worker_state.find({}, {"_id": 0}))