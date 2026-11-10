import os
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
PUBLISH_TO_CHANNEL = os.getenv("PUBLISH_TO_CHANNEL", "false").lower() == "true"
TOP_N = int(os.getenv("TOP_N", "15"))
MIN_HISTORY = int(os.getenv("MIN_HISTORY", "80"))
