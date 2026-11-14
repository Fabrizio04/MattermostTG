import os
import re
import sys
import json
import keyring

from logger import log
from pathlib import Path
from keyring.errors import KeyringError

from func.get_system_locale import get_system_locale

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
    "LOG_LEVEL": "INFO",
    "THEME": "light",
    "LANGUAGE": get_system_locale()
}

VALID_THEMES = {"light", "dark"}
URL_REGEX = re.compile(r"^wss?://[^\s/$.?#].[^\s]*$")
LANG_REGEX = re.compile(r"^[a-z]{2}_[A-Z]{2}$")
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}
SENSITIVE_KEYS = ["MATTERMOST_TOKEN", "TELEGRAM_BOT_TOKEN","AES_ENCRYPTION_KEY"]
HEADLESS_KEYS = ["PORT","HTTP_USER","HTTP_PASS"]

def _load(file_path):
    global config
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                config.update(saved_data)
        except Exception as e:
            from func.i18n import get
            log.error(f"{get('log.settings.error_load')} {e}")

def _load_custom(file_path):
    if not os.path.exists(file_path):
        _load(CONFIG_FILE_PATH)
    else:
        _load(file_path)

def load_settings(args = None):
    global config

    if args and args.headless:
        if args.config == "":
            config["MATTERMOST_WS_URL"] = args.ws_url
            config["MATTERMOST_TOKEN"] = args.token
            config["TELEGRAM_BOT_TOKEN"] = args.bot_token
            config["TELEGRAM_CHAT_ID"] = args.chat_id
            config["EXCLUDED_SENDERS"] = args.excluded_senders
            config["EXCLUDED_CHANNELS"] = args.excluded_channels
            config["ECHO_SUPPRESSION_ENABLED"] = args.echo_suppression
            config["ANONYMOUS_MODE"] = args.anonymous_mode
            config["INCLUDE_SENDER"] = args.include_sender
            config["INCLUDE_CHANNEL"] = args.include_channel
            config["INCLUDE_MESSAGE"] = args.include_message
            config["AES_ENCRYPTION_ENABLED"] = args.aes_enabled
            config["AES_ENCRYPTION_KEY"] = args.aes_key
            config["WS_RECONNECT_TIMEOUT"] = args.ws_val
            config["RETRY_LOGIC_TIMEOUT"] = args.retry_val
            config["RETRY_LOGIC_MAX_ATTEMPTS"] = args.attempts_val
            config["TG_HTTP_TIMEOUT"] = args.tg_http_val
            config["LOG_LEVEL"] = args.log_level
            config["LANGUAGE"] = args.lang
            config["PORT"] = args.port
            config["HTTP_USER"] = args.http_user
            config["HTTP_PASS"] = args.http_pass
        else:
            _load_custom(args.config)
    else:
        _load(CONFIG_FILE_PATH)
        try:
            config["MATTERMOST_TOKEN"] = keyring.get_password(APP_NAME, "MATTERMOST_TOKEN") or ""
            config["TELEGRAM_BOT_TOKEN"] = keyring.get_password(APP_NAME, "TELEGRAM_BOT_TOKEN") or ""
        except (KeyringError, Exception) as e:
            from func.i18n import get
            log.error(f"{get('log.settings.error_keyring')} {e}")
            config["MATTERMOST_TOKEN"] = config.get("MATTERMOST_TOKEN", "")
            config["TELEGRAM_BOT_TOKEN"] = config.get("TELEGRAM_BOT_TOKEN", "")

def handle_imported_sensitive_data():
    """Verifica la presenza di chiavi sensibili nel JSON importato,
    le sposta nel keyring di sistema e le rimuove dal file."""
    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        updated = False        
        
        for json_key in SENSITIVE_KEYS:
            if json_key in data and data[json_key]:
                keyring.set_password(APP_NAME, json_key, data[json_key])
                del data[json_key]
                updated = True
                
        if updated:
            with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        from func.i18n import get
        log.error(f"{get('log.settings.error_sensitive_data')} {e}")

def validate_config(config_data: dict) -> bool:
    """Valida la struttura e i valori di un dizionario di configurazione.
    Restituisce True se tutto è valido altrimenti False.
    """

    # Verifica dict
    if not isinstance(config_data, dict):
        return False

    # Struttura json
    allowed_keys = set(config.keys()).union(set(SENSITIVE_KEYS + HEADLESS_KEYS))
    
    if not set(config_data.keys()).issubset(allowed_keys):
        return False

    try:
        # Stringhe
        str_keys = ["MATTERMOST_WS_URL", "EXCLUDED_SENDERS", "EXCLUDED_CHANNELS"] + SENSITIVE_KEYS
        for s_key in str_keys:
            val = config_data.get(s_key)
            if val is not None and not isinstance(val, str):
                return False

        # URL WebSocket (può essere vuoto o un URL ws:// / wss:// valido)
        ws_url = config_data.get("MATTERMOST_WS_URL", "")
        if ws_url and not URL_REGEX.match(ws_url):
            return False

        # Telegram Chat ID (stringhe/interi)
        if "TELEGRAM_CHAT_ID" in config_data:
            val = config_data.get("TELEGRAM_CHAT_ID")
            if val is not None and not isinstance(val, (str, int)):
                return False

        # Timeout e tentativi (interi positivi)
        for int_key in ["WS_RECONNECT_TIMEOUT", "RETRY_LOGIC_TIMEOUT", "RETRY_LOGIC_MAX_ATTEMPTS", "TG_HTTP_TIMEOUT"]:
            val = config_data.get(int_key)
            if val is not None and not isinstance(val, int):
                return False

        # Flag booleani
        bool_keys = [
            "ECHO_SUPPRESSION_ENABLED", "ANONYMOUS_MODE", "INCLUDE_SENDER",
            "INCLUDE_CHANNEL", "INCLUDE_MESSAGE", "AES_ENCRYPTION_ENABLED", "ALWAYS_ON_TOP"
        ]
        for b_key in bool_keys:
            val = config_data.get(b_key)
            if val is not None and not isinstance(val, bool):
                return False

        # Log Level
        log_level = config_data.get("LOG_LEVEL")
        if log_level is not None and log_level not in VALID_LOG_LEVELS:
            return False

        # Tema
        theme = config_data.get("THEME")
        if theme is not None and theme not in VALID_THEMES:
            return False

        # Lingua (Controllo formato esatto es. it_IT)
        language = config_data.get("LANGUAGE")
        if language is not None and (not isinstance(language, str) or not LANG_REGEX.match(language)):
            return False

        # Ccontrollo srv headless
        for h_key in HEADLESS_KEYS:
            val = config_data.get(h_key)
            if val is not None and not isinstance(val, (str, int)):
                return False

    except Exception as e:
        from func.i18n import get
        log.error(f"{get('log.settings.error_validate_config')} {e}")
        return False

    return True

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
    config["THEME"] = "light"
    config["LANGUAGE"] = get_system_locale()

def save_settings(ws_url, mm_token, tg_token, tg_chat_id, excluded_senders, excluded_channels, echo_suppression, anonymous_mode, include_sender, include_channel, include_message, aes_enabled, always_on_top, ws_val, retry_val, attempts_val, tg_http_val, log_level, theme, lang):
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
    config["THEME"] = theme
    config["LANGUAGE"] = lang

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
                "LOG_LEVEL": log_level,
                "THEME": theme,
                "LANGUAGE": lang
            }, f, indent=4)
        from func.i18n import get
        log.debug(get("log.settings.saved"))
    except Exception as e:
        from func.i18n import get
        log.error(f"{get('log.settings.error_save_settings')} {e}")

    try:
        keyring.set_password(APP_NAME, "MATTERMOST_TOKEN", mm_token)
        keyring.set_password(APP_NAME, "TELEGRAM_BOT_TOKEN", tg_token)
    except (KeyringError, Exception) as e:
        from func.i18n import get
        log.error(f"{get('log.settings.error_save_keyring')} {e}")