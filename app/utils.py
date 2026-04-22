import hashlib
import os
import asyncio
import random

from datetime import datetime, timedelta, timezone

from telethon.errors import FloodWaitError

from parser import is_signal_message
from db import save_signal, state_collection, bulk_save


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
    except Exception:
        # duplicate or DB issue
        pass


async def backfill_channel(client, channel):
    state = get_channel_state(channel)

    if state and state.get("backfill_done"):
        print(f"⏭️ Skipping {channel}, already backfilled")
        return

    last_id = state.get("last_message_id") if state else None

    print(f"📥 Backfilling {channel} from {last_id or 'start'}")

    limit_date = datetime.now(timezone.utc) - timedelta(days=365 * 3)

    async for msg in client.iter_messages(
        channel,
        min_id=last_id if last_id else 0,
        reverse=True
    ):
        try:
            if msg.date < limit_date:
                break

            await process_message(msg, channel)

            # update checkpoint
            update_channel_state(channel, last_id=msg.id)

            # rate limit protection
            await asyncio.sleep(random.uniform(0.3, 0.8))

        except FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

    update_channel_state(channel, done=True)
    print(f"✅ Backfill completed for {channel}")

from pymongo import UpdateOne

BATCH_SIZE = 50   # tune this (50–200 is good)


async def backfill_channel(client, channel):
    state = get_channel_state(channel)

    if state and state.get("backfill_done"):
        print(f"⏭️ Skipping {channel}, already backfilled")
        return

    last_id = state.get("last_message_id") if state else 0

    print(f"📥 Backfilling {channel} from {last_id or 'start'}")

    limit_date = datetime.now(timezone.utc) - timedelta(days=365 * 3)

    batch = []
    last_processed_id = last_id

    async for msg in client.iter_messages(
        channel,
        min_id=last_id,
        reverse=True
    ):
        try:
            if msg.date < limit_date:
                break

            processed = await process_message(msg, channel, return_data=True)
            if processed:
                batch.append(processed)

            last_processed_id = msg.id

            # 🔥 flush batch
            if len(batch) >= BATCH_SIZE:
                await bulk_save(batch)
                update_channel_state(channel, last_id=last_processed_id)
                batch.clear()

                # ⏱ wait BETWEEN batches (not per message)
                await asyncio.sleep(random.uniform(1, 3))

        except FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

    # save remaining
    if batch:
        await bulk_save(batch)
        update_channel_state(channel, last_id=last_processed_id)

    update_channel_state(channel, done=True)
    print(f"✅ Backfill completed for {channel}")