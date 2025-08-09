# GOD CMD Centre — Telegram WebApp + Telethon (Cyberpunk HoloDeck)

This repo boots a Telegram **WebApp** UI and a **Telethon** backend that streams
live messages to your dashboard via **Socket.IO**.

## Quick start (local)

1. Create `.env` from `.env.example` and fill:
   - `API_ID` / `API_HASH` from https://my.telegram.org
   - `BOT_TOKEN` from @BotFather (rotate a fresh token)
2. Install & run:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```
3. Open your bot webapp link (from Telegram):
   `https://t.me/<your_bot_username>/<your_short_name>`

## Deploy (Render example)

1. Push to GitHub.
2. On Render: **New Web Service** → connect repo.
3. Environment: add variables from `.env.example` (DO NOT commit a real `.env`).
4. Build command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start command:
   ```bash
   python app.py
   ```
6. Take the Render HTTPS URL and (optionally) set it in @BotFather **Web App URL**.

## Notes
- Frontend verifies Telegram WebApp `initData` via `/verify` before allowing use.
- Backend listens account-wide with Telethon and emits:
  - `live_feed` — new messages
  - `keyword_alert` — first matching keyword in `KEYWORDS`
  - `media_item` — placeholder for media (wire a CDN later)
