import hashlib
import os

from parser import is_signal_message
from db import save_signal, state_collection


MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

def generate_hash(msg):
    text = msg.text or ""
    base = f"{msg.id}|{msg.date.isoformat()}|{text}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def get_channel_state(channel):
    return state_collection.find_one({"channel": channel})


def update_channel_state(channel, last_id=None, done=None):
    update = {}

    if last_id is not None:
        update["last_message_id"] = last_id

    if done is not None:
        update["backfill_done"] = done

    state_collection.update_one(
        {"channel": channel},
        {"$set": update},
        upsert=True
    )


async def process_message(msg, channel):
    has_text = bool(msg.text)
    # has_media = bool(msg.media)

    # if not has_text and not has_media:
    #     return
    media_path = None
    if not has_text:
        return
    
    if not has_text or not is_signal_message(msg.text):
        data = {
        "type": "other",
        "channel": channel,
        "message_id": msg.id,
        "date": msg.date,
        "text": msg.text,
        "media_path": media_path,
        "hash": generate_hash(msg),
        } 
    # if has_media:
    #     media_path = await msg.download_media(
    #         file=f"{MEDIA_DIR}/{msg.id}"
    #     )
    else:
        data = {
            "type": "signal",
            "channel": channel,
            "message_id": msg.id,
            "date": msg.date,
            "text": msg.text,
            "media_path": media_path,
            "hash": generate_hash(msg),
        }
       
    try:
        save_signal(data)
        print(f"✅ Saved signal {msg.id} ")
        return data
    except Exception:
        # duplicate or DB issue
        pass


