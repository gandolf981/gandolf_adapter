import re

def is_signal_message(text: str) -> bool:
    text = text.lower()

    patterns = [
        r"(buy|sell|long|short)",  
        r"(tp|take profit)",      
        r"(sl|stop loss)",       
        r"\d+\.\d+", 
    ]

    score = sum(bool(re.search(p, text)) for p in patterns)

    return score >= 3

def parse_session_string(raw: str):
    name, api_id, api_hash, session_string = raw.split("|")

    return {
        "name": name,
        "api_id": int(api_id),
        "api_hash": api_hash,
        "session_string": session_string
    }