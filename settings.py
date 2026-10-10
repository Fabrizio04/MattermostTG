import os
import json
import keyring

from keyring.errors import KeyringError
from logger import log

# --- COSTANTI & CONFIGURAZIONE ---
APP_NAME = "MattermostNotifier"
CONFIG_FILE = "settings.json"

config = {
    "MATTERMOST_WS_URL": "",
    "TELEGRAM_CHAT_ID": "",
    "EXCLUDED_SENDERS": "",
    "EXCLUDED_CHANNELS": "",
    "ECHO_SUPPRESSION_ENABLED": True
}

# --- CARICAMENTO / SALVATAGGIO SICURO ---
def load_settings():
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
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


def save_settings(ws_url, mm_token, tg_token, tg_chat_id, excluded_senders, excluded_channels, echo_suppression):
    global config
    config["MATTERMOST_WS_URL"] = ws_url
    config["TELEGRAM_CHAT_ID"] = tg_chat_id
    config["MATTERMOST_TOKEN"] = mm_token
    config["TELEGRAM_BOT_TOKEN"] = tg_token
    config["EXCLUDED_SENDERS"] = excluded_senders
    config["EXCLUDED_CHANNELS"] = excluded_channels
    config["ECHO_SUPPRESSION_ENABLED"] = echo_suppression

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "MATTERMOST_WS_URL": ws_url,
                "TELEGRAM_CHAT_ID": tg_chat_id,
                "EXCLUDED_SENDERS": excluded_senders,
                "EXCLUDED_CHANNELS": excluded_channels,
                "ECHO_SUPPRESSION_ENABLED": echo_suppression
            }, f, indent=4)
        log.debug("Impostazioni salvate con successo.")
    except Exception as e:
        log.error(f"Errore salvataggio json: {e}")

    try:
        keyring.set_password(APP_NAME, "MATTERMOST_TOKEN", mm_token)
        keyring.set_password(APP_NAME, "TELEGRAM_BOT_TOKEN", tg_token)
    except (KeyringError, Exception) as e:
        log.error(f"Errore salvataggio keyring: {e}")