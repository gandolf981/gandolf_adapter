import asyncio
import os

from telethon import TelegramClient, events


from utils import process_message, backfill_channel
from config import API_ID, API_HASH, CHANNELS, PROXY



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



async def main():
    client = TelegramClient(
        "./session",   
        API_ID,
        API_HASH,
        proxy=PROXY,
        connection_retries=5,
    )

    await client.connect()

    if not await client.is_user_authorized():
        raise Exception("❌ Session not authorized. Run login once.")

    print("🚀 Telegram client started")

    register_listener(client)


    await run_backfill(client)

    print("👂 Listening for new signals...")
    await client.run_until_disconnected()


async def runner():
    while True:
        try:
            await main()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Restarting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(runner())