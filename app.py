import os, hmac, hashlib
from urllib.parse import parse_qsl
from dotenv import load_dotenv
from flask import Flask, send_from_directory, request, abort
from flask_socketio import SocketIO
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_NAME = os.getenv("SESSION_NAME", "godcmd")
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
PORT = int(os.getenv("PORT", "5000"))

app = Flask(__name__, static_folder="web")
# eventlet async mode for Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def verify_init_data(init_data: str) -> bool:
    """Verify Telegram WebApp initData per Telegram docs."""
    try:
        parts = dict(parse_qsl(init_data, strict_parsing=True))
        check_hash = parts.pop("hash", "")
        data_check_string = "\n".join(f"{k}={parts[k]}" for k in sorted(parts))
        secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
        computed = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, check_hash)
    except Exception:
        return False

@app.get("/")
def index():
    return send_from_directory("web", "index.html")

@app.post("/verify")
def verify():
    init_data = request.form.get("initData", "")
    if not init_data or not verify_init_data(init_data):
        abort(403)
    return "ok"

# Telethon client for your account
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage)
async def on_new_message(ev):
    try:
        text = ev.raw_text or ""
        sender = await ev.get_sender()
        username = (sender.username if sender and sender.username else f"id:{getattr(sender,'id','?')}")
        chat = (await ev.get_chat()).title if ev.chat else "Private"
        socketio.emit("live_feed", {"sender": username, "text": text, "chat": chat})

        low = text.lower()
        for kw in KEYWORDS:
            if kw and kw in low:
                socketio.emit("keyword_alert", {"keyword": kw, "chat": chat})
                break

        if ev.photo or ev.media:
            # TODO: persist media, serve via CDN, emit URL
            socketio.emit("media_item", {"url": ""})
    except Exception as e:
        print("handler error:", e)

if __name__ == "__main__":
    with client:
        socketio.run(app, host="0.0.0.0", port=PORT)
