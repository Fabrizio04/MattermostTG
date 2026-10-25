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
    """
    Determina il livello di log iniziale:
    - Se headless:
        1. Cerca un file di configurazione custom (--config o ENV CONFIG_PATH).
        2. Se assente, cerca --log-level da CLI.
        3. Se assente, cerca nella ENV (LOG_LEVEL).
    - Se non headless (GUI):
        - Legge direttamente dal file di configurazione standard JSON (CONFIG_FILE_PATH).
    - Fallback finale: "INFO".
    """

    is_headless = "--headless" in sys.argv or os.getenv("HEADLESS", "false").lower() == "true"

    if is_headless:
        custom_config = None
        try:
            if "--config" in sys.argv:
                idx = sys.argv.index("--config")
                if idx + 1 < len(sys.argv):
                    custom_config = sys.argv[idx + 1]
        except Exception:
            pass

        if not custom_config:
            custom_config = os.getenv("CONFIG_PATH", "")

        if custom_config:
            try:
                if os.path.exists(custom_config):
                    with open(custom_config, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "LOG_LEVEL" in data:
                            return data["LOG_LEVEL"].upper()
                elif os.path.exists(CONFIG_FILE_PATH):
                    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "LOG_LEVEL" in data:
                            return data["LOG_LEVEL"].upper()
            except Exception:
                pass

        try:
            if "--log-level" in sys.argv:
                idx = sys.argv.index("--log-level")
                if idx + 1 < len(sys.argv):
                    cli_level = sys.argv[idx + 1]
                    if cli_level:
                        return cli_level.upper()
        except Exception:
            pass

        env_level = os.getenv("LOG_LEVEL", "")
        if env_level:
            return env_level.upper()
        
    else:
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