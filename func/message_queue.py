import time
import queue
import threading

from logger import log
from settings import config

# Coda thread-safe per i messaggi non inviati
message_retry_queue = queue.Queue()

# Flag per il controllo del thread worker
_worker_running = True
_worker_thread = None

class FailedMessage:
    def __init__(self, notification_msg: str):
        self.notification_msg = notification_msg
        self.attempts = 0
        self.created_at = time.time()

def enqueue_failed_message(notification_msg: str):
    """
    Aggiunge un messaggio fallito alla coda di tentativi.
    """
    msg_obj = FailedMessage(notification_msg)
    message_retry_queue.put(msg_obj)
    log.warning(f"Messaggio aggiunto alla coda di retry (Elementi in coda: {message_retry_queue.qsize()})")

def _retry_worker():
    """
    Thread worker che ciclicamente controlla la coda e ritenta l'invio.
    """
    from func.message import send_telegram  # Import locale per evitare import circolare

    global _worker_running
    log.debug("Worker Retry Logic avviato.")

    while _worker_running:
        # Recupera i timeout e max tentativi aggiornati dalle config
        retry_interval = int(config.get("RETRY_LOGIC_TIMEOUT", 10))
        max_attempts = int(config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5))

        if not message_retry_queue.empty():
            msg_obj = message_retry_queue.get()

            if msg_obj.attempts >= max_attempts:
                log.error(
                    f"Messaggio scartato: raggiunto il limite massimo di {max_attempts} tentativi. "
                    f"Testo: {msg_obj.notification_msg[:30]}..."
                )
                message_retry_queue.task_done()
                continue

            msg_obj.attempts += 1
            log.info(
                f"Tentativo {msg_obj.attempts}/{max_attempts} per il messaggio in coda "
                f"(Elementi rimasti: {message_retry_queue.qsize() + 1})..."
            )

            # Tenta il reinvio verso Telegram
            success = send_telegram(msg_obj.notification_msg, is_retry=True)

            if success:
                log.info(f"Messaggio in coda inviato con successo al tentativo {msg_obj.attempts}.")
                message_retry_queue.task_done()
            else:
                log.warning(f"Invio fallito per il messaggio in coda (tentativo {msg_obj.attempts}). Re-inserimento in coda.")
                # Rimettiamo il messaggio in fondo alla coda per riprovare al prossimo ciclo
                message_retry_queue.put(msg_obj)
                message_retry_queue.task_done()

        # Attesa configurabile prima del prossimo ciclo
        time.sleep(retry_interval)

def start_retry_worker():
    """
    Avvia il thread worker se non è già attivo.
    """
    global _worker_thread, _worker_running
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_running = True
        _worker_thread = threading.Thread(target=_retry_worker, daemon=True)
        _worker_thread.start()

def stop_retry_worker():
    """
    Mette in pausa/ferma il worker.
    """
    global _worker_running
    _worker_running = False