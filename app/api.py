# api.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from state import STATE
from datetime import datetime

app = FastAPI()


@app.get("/state")
def get_state():
    return STATE


@app.get("/", response_class=HTMLResponse)
def dashboard():
    color = {
        "running": "#16a34a",
        "error": "#dc2626",
        "starting": "#f59e0b"
    }.get(STATE["status"], "#6b7280")

    html = f"""
    <html>
    <head>
        <title>Worker Dashboard</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body {{
                font-family: Arial;
                background: #0f172a;
                color: white;
                padding: 20px;
            }}
            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
            }}
            .title {{
                font-size: 22px;
                margin-bottom: 10px;
            }}
            .status {{
                color: {color};
                font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <div class="card">
            <div class="title">🚀 Worker Status</div>
            Status: <span class="status">{STATE["status"]}</span><br>
            Session: {STATE["session"]}<br>
            Mode: {STATE["mode"]}
        </div>

        <div class="card">
            <div class="title">📡 Activity</div>
            Channel: {STATE["current_channel"]}<br>
            Last Message ID: {STATE["last_message_id"]}
        </div>

        <div class="card">
            <div class="title">⏱ Last Update</div>
            {STATE["updated_at"]}
        </div>

    </body>
    </html>
    """
    return html