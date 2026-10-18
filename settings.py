import os
import json
import keyring

from logger import log
from pathlib import Path
from keyring.errors import KeyringError

# --- COSTANTI & CONFIGURAZIONE ---
APP_NAME = "MattermostNotifier"

APP_DIR = Path.home() / ".mattermost_notifier"
try:
    APP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

CONFIG_FILE_PATH = os.path.join(APP_DIR, "mattermosttg.json")

config = {
    "MATTERMOST_WS_URL": "",
    "TELEGRAM_CHAT_ID": "",
    "EXCLUDED_SENDERS": "",
    "EXCLUDED_CHANNELS": "",
    "ECHO_SUPPRESSION_ENABLED": True,
    "ANONYMOUS_MODE": False,
    "INCLUDE_SENDER": True,
    "INCLUDE_CHANNEL": True,
    "INCLUDE_MESSAGE": True,
    "AES_ENCRYPTION_ENABLED": False,
    "ALWAYS_ON_TOP": False,
    "WS_RECONNECT_TIMEOUT": 5,
    "RETRY_LOGIC_TIMEOUT": 10,
    "RETRY_LOGIC_MAX_ATTEMPTS": 5,
    "TG_HTTP_TIMEOUT": 5,
    "LOG_LEVEL": "INFO"
}

# --- CARICAMENTO / SALVATAGGIO SICURO ---
def load_settings():
    global config
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                config.update(saved_data)
        except Exception as e:
            log.error(f"Errore caricamento json: {e}")

    try:
        config["MATTERMOST_TOKEN"] = keyring.get_password(APP_NAME, "MATTERMOST_TOKEN") or ""
        config["TELEGRAM_BOT_TOKEN"] = keyring.get_password(APP_NAME, "TELEGRAM_BOT_TOKEN") or ""
    except (KeyringError, Exception) as e:
        log.error(f"Errore caricamento keyring (sistema o backend non supportato): {e}")
        config["MATTERMOST_TOKEN"] = config.get("MATTERMOST_TOKEN", "")
        config["TELEGRAM_BOT_TOKEN"] = config.get("TELEGRAM_BOT_TOKEN", "")


def reset_settings():
    global config
    config["MATTERMOST_WS_URL"] = ""
    config["TELEGRAM_CHAT_ID"] = ""
    config["MATTERMOST_TOKEN"] = ""
    config["TELEGRAM_BOT_TOKEN"] = ""
    config["EXCLUDED_SENDERS"] = ""
    config["EXCLUDED_CHANNELS"] = ""
    config["ECHO_SUPPRESSION_ENABLED"] = True
    config["ANONYMOUS_MODE"] = False
    config["INCLUDE_SENDER"] = True
    config["INCLUDE_CHANNEL"] = True
    config["INCLUDE_MESSAGE"] = True
    config["AES_ENCRYPTION_ENABLED"] = False
    config["ALWAYS_ON_TOP"] = False
    config["WS_RECONNECT_TIMEOUT"] = 5
    config["RETRY_LOGIC_TIMEOUT"] = 10
    config["RETRY_LOGIC_MAX_ATTEMPTS"] = 5
    config["TG_HTTP_TIMEOUT"] = 5
    config["LOG_LEVEL"] = "INFO"
    import logging
    log.setLevel(logging.INFO)


def save_settings(ws_url, mm_token, tg_token, tg_chat_id, excluded_senders, excluded_channels, echo_suppression, anonymous_mode, include_sender, include_channel, include_message, aes_enabled, always_on_top, ws_val, retry_val, attempts_val, tg_http_val, log_level):
    global config
    config["MATTERMOST_WS_URL"] = ws_url
    config["TELEGRAM_CHAT_ID"] = tg_chat_id
    config["MATTERMOST_TOKEN"] = mm_token
    config["TELEGRAM_BOT_TOKEN"] = tg_token
    config["EXCLUDED_SENDERS"] = excluded_senders
    config["EXCLUDED_CHANNELS"] = excluded_channels
    config["ECHO_SUPPRESSION_ENABLED"] = echo_suppression
    config["ANONYMOUS_MODE"] = anonymous_mode
    config["INCLUDE_SENDER"] = include_sender
    config["INCLUDE_CHANNEL"] = include_channel
    config["INCLUDE_MESSAGE"] = include_message
    config["AES_ENCRYPTION_ENABLED"] = aes_enabled
    config["ALWAYS_ON_TOP"] = always_on_top
    config["WS_RECONNECT_TIMEOUT"] = ws_val
    config["RETRY_LOGIC_TIMEOUT"] = retry_val
    config["RETRY_LOGIC_MAX_ATTEMPTS"] = attempts_val
    config["TG_HTTP_TIMEOUT"] = tg_http_val
    config["LOG_LEVEL"] = log_level

    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "MATTERMOST_WS_URL": ws_url,
                "TELEGRAM_CHAT_ID": tg_chat_id,
                "EXCLUDED_SENDERS": excluded_senders,
                "EXCLUDED_CHANNELS": excluded_channels,
                "ECHO_SUPPRESSION_ENABLED": echo_suppression,
                "ANONYMOUS_MODE": anonymous_mode,
                "INCLUDE_SENDER": include_sender,
                "INCLUDE_CHANNEL": include_channel,
                "INCLUDE_MESSAGE": include_message,
                "AES_ENCRYPTION_ENABLED": aes_enabled,
                "ALWAYS_ON_TOP": always_on_top,
                "WS_RECONNECT_TIMEOUT": ws_val,
                "RETRY_LOGIC_TIMEOUT": retry_val,
                "RETRY_LOGIC_MAX_ATTEMPTS": attempts_val,
                "TG_HTTP_TIMEOUT": tg_http_val,
                "LOG_LEVEL": log_level
            }, f, indent=4)
        log.debug("Impostazioni salvate con successo.")
    except Exception as e:
        log.error(f"Errore salvataggio json: {e}")

    try:
        keyring.set_password(APP_NAME, "MATTERMOST_TOKEN", mm_token)
        keyring.set_password(APP_NAME, "TELEGRAM_BOT_TOKEN", tg_token)
    except (KeyringError, Exception) as e:
        log.error(f"Errore salvataggio keyring: {e}")