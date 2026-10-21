import os
import base64
import keyring

from logger import log
from func.i18n import get
from settings import APP_NAME, config
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_or_create_aes_key():
    key_hex = keyring.get_password(APP_NAME, "AES_ENCRYPTION_KEY")

    if not key_hex:
        key_bytes = os.urandom(32)
        key_hex = key_bytes.hex()
        try:
            keyring.set_password(APP_NAME, "AES_ENCRYPTION_KEY", key_hex)
        except Exception as e:
            log.error(f"{get("log.aes.error_save_keyring")} {e}")
    return key_hex

def aes(payload):

    if not config.get("AES_ENCRYPTION_ENABLED", False):
        return ""

    try:
        CHIAVE_HEX = get_or_create_aes_key()

        if not CHIAVE_HEX:
            raise Exception("Chiave AES non disponibile")

        chiave = bytes.fromhex(CHIAVE_HEX)

        nonce = os.urandom(12)
        aesgcm = AESGCM(chiave)
        testo_cifrato = aesgcm.encrypt(nonce, payload.encode('utf-8'), None)

        pacchetto = nonce + testo_cifrato
        payload_base64 = base64.b64encode(pacchetto).decode('utf-8')

        return f"`{payload_base64}`"

    except Exception as e:
        log.error(f"{get("log.aes.error_execution")} {e}")
        return ""
