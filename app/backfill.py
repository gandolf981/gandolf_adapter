import asyncio
import random

from datetime import datetime, timedelta, timezone

from telethon.errors import FloodWaitError
from utils import get_channel_state, process_message, update_channel_state
from db import bulk_save
from  state_manager import update_state

BATCH_SIZE = 50   # tune this (50–200 is good)

async def backfill_channel(client, channel, session_name):
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

            processed = await process_message(msg, channel)
            if processed:
                batch.append(processed)

            last_processed_id = msg.id

            # 🔥 flush batch
            if len(batch) >= BATCH_SIZE:
                bulk_save(batch)
                update_channel_state(channel, last_id=last_processed_id)
                update_state(session_name, {
                "mode": "backfilling",
                "current_channel": channel,
                "last_message_id": msg.id,
                })
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