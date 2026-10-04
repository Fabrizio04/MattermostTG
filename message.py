import requests

from logger import log
from settings import config

def send_telegram(text):
    bot_token = config.get("TELEGRAM_BOT_TOKEN")
    chat_id = config.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        log.error("Token Telegram o Chat ID mancanti!")
        return
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
        log.info("Notifica inviata con successo su Telegram")
    except Exception as e:
        log.error(f"Errore invio Telegram: {e}")