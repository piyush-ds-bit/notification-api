# ✅ FastAPI app to receive Supabase webhook and send Telegram notification

from fastapi import FastAPI, Request, Header, HTTPException
import httpx
import os
app = FastAPI()

# Telegram Bot Token & Your Chat ID (replace these securely via env vars or directly here)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_telegram_chat_id")

# Optional: simple token-based security
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET", "your_secret_token")


@app.get("/")
def hello():
    return {"message":"Supabase to Telegram notification mangament API"}

@app.get("/about")
def about():
    return {"description":"A full functional API to manage my messages and visitor logs notification via Telegram"}


@app.post("/send-telegram")
async def send_telegram(request: Request, x_webhook_secret: str = Header(...)):
    if x_webhook_secret != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    payload = await request.json()

    # Detect a source: contact_messages or visitor_logs
    table = payload.get("table", {}).get("name", "unknown")
    record = payload.get("record", {})

    if table == "contact_messages":
        name = record.get("name", "Someone")
        email = record.get("email", "[No Email]")
        message_text = record.get("message", "[No Message]")
        msg = f"\ud83d\udce9 <b>New Contact Message</b>\n<b>Name:</b> {name}\n<b>Email:</b> {email}\n<b>Message:</b> {message_text}"

    elif table == "visitor_logs":
        visited_at = record.get("visited_at", "[No Time]")
        page = record.get("page", "Unknown Page")
        msg = f"\ud83d\udcca <b>New Visitor Log</b>\n<b>Page:</b> {page}\n<b>Time:</b> {visited_at}"

    else:
        msg = f"\u2757 <b>Unknown Notification</b>\n{record}"

    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(telegram_api_url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        })

    return {"status": "sent to telegram"}
