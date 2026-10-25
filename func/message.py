import requests

from logger import log
from settings import config
from func.message_queue import enqueue_failed_message
from func.i18n import get

def send_telegram(text: str, is_retry: bool = False) -> bool:
    """
    Invia un messaggio a Telegram.
    Restituisce True se ha successo altrimenti False.
    """

    bot_token = config.get("TELEGRAM_BOT_TOKEN")
    chat_id = config.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        log.error(get("log.message.missing_tk_id"))
        return
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, json=payload, timeout=int(config.get("TG_HTTP_TIMEOUT", 5)))

        if response.status_code == 200:
            log.info(get("log.message.notify_sent"))
            return True
        else:
            log.error(f"{get('log.message.http_error')} {response.status_code}: {response.text}")
        
    except Exception as e:
        log.error(f"{get('log.message.error')} {e}")

    if not is_retry:
        enqueue_failed_message(text)

    return False