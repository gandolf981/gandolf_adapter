import asyncio
import os
import threading
import uvicorn

from telethon import TelegramClient, events
from worker import acquire_session, release_stale_sessions

from api import app
from state import STATE
from utils import process_message, backfill_channel
from config import CHANNELS, PROXY
from client_generator import create_client
from session_db_generator import load_sessions_from_env


def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def run_backfill(client):
    for channel in CHANNELS:
        await backfill_channel(client, channel)


def register_listener(client):
    @client.on(events.NewMessage(chats=CHANNELS))
    async def handler(event):
        channel = event.chat.username or str(event.chat_id)

        try:
            await process_message(event.message, channel)
        except Exception as e:
            print(f"⚠️ Listener error: {e}")

SESSION=None
async def runner():
    global SESSION

    load_sessions_from_env()
    release_stale_sessions()
    SESSION = acquire_session()

    if not SESSION:
        print("No session available")
        return

    while True:
        try:
            client = create_client(SESSION)
            await client.connect()

            if not await client.is_user_authorized():
                raise Exception("Not authorized")

            register_listener(client)
            await run_backfill(client)

            await client.run_until_disconnected()

        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 reconnecting same session in 5 sec...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(runner())