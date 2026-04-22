import asyncio
import threading
import uvicorn

from telethon import events
from worker import acquire_session, release_stale_sessions

from api import app
from backfill import backfill_channel
from utils import process_message
from config import CHANNELS
from client_generator import create_client
from state_manager import update_state
from session_db_generator import load_sessions_from_env


def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)


async def run_backfill(client, session_name):
    for channel in CHANNELS:
        await backfill_channel(client, channel, session_name)
    return True

def register_listener(client, session_name):
    @client.on(events.NewMessage(chats=CHANNELS))

    async def handler(event):
        channel = event.chat.username or str(event.chat_id)
        update_state(session_name, {
            "mode": "listening",
            "current_channel": channel,
        })
        try:
            await process_message(event.message, channel)
        except Exception as e:
            print(f"⚠️ Listener error: {e}")


SESSION = None


async def runner():
    global SESSION

    load_sessions_from_env()
    release_stale_sessions()

    SESSION = acquire_session()

    if not SESSION:
        print("❌ No session available")
        return

    print(f"✅ Using session: {SESSION['name']}")

    while True:
        try:
            client = create_client(SESSION)
            await client.connect()

            if not await client.is_user_authorized():
                raise Exception("Not authorized")

            print("🚀 Telegram client started")

            register_listener(client, SESSION["name"])
            await run_backfill(client, SESSION["name"])

            print("👂 Listening...")
            await client.run_until_disconnected()

        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 reconnecting same session in 5 sec...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    asyncio.run(runner())