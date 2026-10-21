import os
import sys
import json
import logging

from pathlib import Path

APP_DIR = Path.home() / ".mattermost_notifier"
try:
    APP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

LOG_FILE_PATH = os.path.join(APP_DIR, "mattermosttg.log")
CONFIG_FILE_PATH = os.path.join(APP_DIR, "mattermosttg.json")

def get_initial_log_level():
    """Legge direttamente il livello di log dal JSON salvato, se esiste."""

    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("LOG_LEVEL", "INFO").upper()
        except Exception:
            pass

    return "INFO"

def setup_logger():
    """
    Configura il logger per stampare a schermo e salvare su file.
    Livelli supportati: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
    """

    logger = logging.getLogger("MattermostNotifier")
    level_str = get_initial_log_level()
    
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }

    logger.setLevel(level_map.get(level_str, logging.INFO))

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", 
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Impossibile creare il file di log: {e}")

    return logger

log = setup_logger()