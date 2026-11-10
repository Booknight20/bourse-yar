import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHANNEL_ID, PUBLISH_TO_CHANNEL

def send_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True}, timeout=25)
    r.raise_for_status()
    return True

def publish_report(text):
    sent = False
    if TELEGRAM_CHAT_ID:
        send_message(TELEGRAM_CHAT_ID, text); sent = True
    if PUBLISH_TO_CHANNEL and TELEGRAM_CHANNEL_ID:
        send_message(TELEGRAM_CHANNEL_ID, text); sent = True
    return sent
