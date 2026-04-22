import os
from parser import parse_session_string
from db import save_session
def load_sessions_from_env():
    sessions_list = []

    for key, value in os.environ.items():
        if key.startswith("SESSION_"):
           save_session(**parse_session_string(value))

    return sessions_list