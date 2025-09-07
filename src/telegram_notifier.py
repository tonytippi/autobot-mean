import os, requests
from dotenv import load_dotenv
load_dotenv()

TG_SEND = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"

def send(text: str):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("[WARN] TELEGRAM_CHAT_ID missing; message not sent.")
        return
    try:
        r = requests.post(TG_SEND, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }, timeout=10)
        if r.status_code != 200:
            print("[ERROR] Telegram send failed:", r.text)
    except Exception as e:
        print("[ERROR] Telegram send error:", repr(e))
