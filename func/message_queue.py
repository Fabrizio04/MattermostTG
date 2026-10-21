import time
import queue
import threading

from logger import log
from func.i18n import get
from settings import config
from model.FailedMessage import FailedMessage

message_retry_queue = queue.Queue()
_worker_running = True
_worker_thread = None

def enqueue_failed_message(notification_msg: str):
    """
    Aggiunge un messaggio fallito alla coda di tentativi.
    """

    msg_obj = FailedMessage(notification_msg)
    message_retry_queue.put(msg_obj)
    log.warning(get("log.message_queue.added").format(qsize=message_retry_queue.qsize()))

def _retry_worker():
    """
    Thread worker che ciclicamente controlla la coda e ritenta l'invio.
    """
    from func.message import send_telegram

    global _worker_running
    log.debug(get("log.message_queue.start"))

    while _worker_running:
        retry_interval = int(config.get("RETRY_LOGIC_TIMEOUT", 10))
        max_attempts = int(config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5))

        if not message_retry_queue.empty():
            msg_obj = message_retry_queue.get()

            if msg_obj.attempts >= max_attempts:
                log.error(f"{get("log.message_queue.discarded").format(max_attempts=max_attempts)}{get("log.message_queue.discarded_text").format(msg=msg_obj.notification_msg[:30])}")
                message_retry_queue.task_done()
                continue

            msg_obj.attempts += 1
            log.info(f"{get("log.message_queue.attempts").format(attempts=msg_obj.attempts, max_attempts=max_attempts)}{get("log.message_queue.remaining").format(qsize=(message_retry_queue.qsize() + 1))}")

            success = send_telegram(msg_obj.notification_msg, is_retry=True)

            if success:
                log.info(get("log.message_queue.msg_sent").format(attempts=msg_obj.attempts))
                message_retry_queue.task_done()
            else:
                log.warning(get("log.message_queue.meg_sent_fail").format(attempts=msg_obj.attempts))
                message_retry_queue.put(msg_obj)
                message_retry_queue.task_done()

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