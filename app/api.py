# api.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from state_manager import get_state

app = FastAPI()


@app.get("/state")
def state():
    return get_state()

@app.get("/", response_class=HTMLResponse)
def dashboard():
    states = get_state()

    cards = ""

    for s in states:
        color = {
            "running": "#16a34a",
            "error": "#dc2626",
            "starting": "#f59e0b"
        }.get(s.get("status"), "#6b7280")

        cards += f"""
        <div class="card">
            <div class="title">🚀 {s.get("worker_id")}</div>
            Status: <span style="color:{color}">{s.get("status")}</span><br>
            Session: {s.get("session")}<br>
            Mode: {s.get("mode")}<br>
            Channel: {s.get("current_channel")}<br>
            Last Msg: {s.get("last_message_id")}<br>
            Updated: {s.get("updated_at")}
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Workers Dashboard</title>
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
                font-size: 20px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        {cards}
    </body>
    </html>
    """