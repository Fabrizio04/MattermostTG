import os
import sys
import base64
import keyring

from logger import log
from func.i18n import get
from settings import APP_NAME, APP_DIR, config
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CONFIG_FILE_PATH = os.path.join(APP_DIR, "mattermosttg.json")

def _new_fs_key():
    key_path = os.path.join(APP_DIR, f"{get('settings.aes.key.filename')}.txt")
    
    if os.path.exists(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                key_hex = f.read().strip()
                if key_hex:
                    return key_hex
        except Exception as e:
            log.error(f"{get('log.aes.error_fs_read')} {e}")

    key_bytes = os.urandom(32)
    key_hex = key_bytes.hex()

    try:
        with open(key_path, "w", encoding="utf-8") as f:
            f.write(key_hex)
        log.debug(get("log.aes.key_saved"))
    except Exception as e:
        log.error(f"{get('log.aes.error_fs_save')} {e}")

    return key_hex

def get_or_create_aes_key():

    is_headless = "--headless" in sys.argv or os.getenv("HEADLESS", "false").lower() == "true"

    if is_headless:
        aes_key = config.get("AES_ENCRYPTION_KEY", "").strip()

        if aes_key:
            return aes_key
        else:
            return _new_fs_key()
    else:
        key_hex = keyring.get_password(APP_NAME, "AES_ENCRYPTION_KEY")

        if not key_hex:
            key_bytes = os.urandom(32)
            key_hex = key_bytes.hex()
            try:
                keyring.set_password(APP_NAME, "AES_ENCRYPTION_KEY", key_hex)
            except Exception as e:
                log.error(f"{get('log.aes.error_save_keyring')} {e}")
        return key_hex

def aes(payload):

    if not config.get("AES_ENCRYPTION_ENABLED", False):
        return ""

    try:
        CHIAVE_HEX = get_or_create_aes_key()

        if not CHIAVE_HEX:
            raise Exception(get("log.aes.error_key_unavailable"))

        chiave = bytes.fromhex(CHIAVE_HEX)

        nonce = os.urandom(12)
        aesgcm = AESGCM(chiave)
        testo_cifrato = aesgcm.encrypt(nonce, payload.encode('utf-8'), None)

        pacchetto = nonce + testo_cifrato
        payload_base64 = base64.b64encode(pacchetto).decode('utf-8')

        return f"`{payload_base64}`"

    except Exception as e:
        log.error(f"{get('log.aes.error_execution')} {e}")
        return ""
