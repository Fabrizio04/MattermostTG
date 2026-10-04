import sys
import logging

# Configurazione del logger di sistema
LOG_FILENAME = "app.log"

def setup_logger(level=logging.INFO):
    """
    Configura il logger per stampare a schermo e salvare su file.
    Livelli supportati: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
    """
    logger = logging.getLogger("MattermostNotifier")
    logger.setLevel(level)

    # Se il logger ha già handler configurati, evita di duplicarli
    if logger.hasHandlers():
        return logger

    # Formato dell'output del log
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", 
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    # Handler 1: Stampa in console (CMD / Terminale)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler 2: Salvataggio su file di log (opzionale ma utilissimo)
    try:
        file_handler = logging.FileHandler(LOG_FILENAME, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Impossibile creare il file di log: {e}")

    return logger

# Istanza globale subito pronta all'uso
log = setup_logger(logging.INFO)

# Esempi di utilizzo:

# log.info("Notifica inviata con successo su Telegram")
# log.debug("Ricevuto nuovo payload dal WebSocket: %s", data)
# log.warning("Servizio in pausa: notifica ignorata")
# log.error("Errore invio Telegram: %s", e)