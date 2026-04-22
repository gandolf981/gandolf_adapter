from telethon.sessions import StringSession
from telethon import TelegramClient
from config import PROXY

def create_client(session_doc):
    return TelegramClient(
        StringSession(session_doc["session_string"]),
        session_doc["api_id"],
        session_doc["api_hash"],
        proxy=PROXY,
        connection_retries=5,
    )