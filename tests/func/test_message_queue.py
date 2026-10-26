import time
from func import message_queue
from unittest.mock import patch, MagicMock
from model.FailedMessage import FailedMessage

def test_failed_message_model():
    msg_text = "Test notifica fallita"
    t_before = time.time()
    fm = FailedMessage(msg_text)
    t_after = time.time()

    assert fm.notification_msg == msg_text
    assert fm.attempts == 0
    assert t_before <= fm.created_at <= t_after

def test_enqueue_failed_message(monkeypatch):
    while not message_queue.message_retry_queue.empty():
        message_queue.message_retry_queue.get()

    with patch("func.message_queue.log.warning") as mock_log, \
         patch("func.message_queue.get", return_value="Queue size: {qsize}"):
        
        message_queue.enqueue_failed_message("Messaggio di errore")
        
        assert message_queue.message_retry_queue.qsize() == 1
        item = message_queue.message_retry_queue.get()
        assert isinstance(item, FailedMessage)
        assert item.notification_msg == "Messaggio di errore"
        mock_log.assert_called_once()

def test_worker_lifecycle(monkeypatch):
    monkeypatch.setattr(message_queue, "_worker_running", False)
    message_queue._worker_thread = None

    with patch("threading.Thread") as mock_thread_class:
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance

        message_queue.start_retry_worker()
        
        assert message_queue._worker_running is True
        mock_thread_class.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    message_queue.stop_retry_worker()
    assert message_queue._worker_running is False

@patch("func.message_queue.time.sleep", side_effect=InterruptedError)
@patch("func.message.send_telegram")
def test_retry_worker_success(mock_send_telegram, mock_sleep, monkeypatch):
    monkeypatch.setattr(message_queue, "config", {"RETRY_LOGIC_TIMEOUT": 1, "RETRY_LOGIC_MAX_ATTEMPTS": 3})
    monkeypatch.setattr(message_queue, "_worker_running", True)
    
    while not message_queue.message_retry_queue.empty():
        message_queue.message_retry_queue.get()
    
    fm = FailedMessage("Riprova questo")
    message_queue.message_retry_queue.put(fm)
    
    mock_send_telegram.return_value = True

    try:
        message_queue._retry_worker()
    except InterruptedError:
        pass

    mock_send_telegram.assert_called_once_with("Riprova questo", is_retry=True)
    assert fm.attempts == 1

@patch("func.message_queue.time.sleep", side_effect=InterruptedError)
@patch("func.message.send_telegram")
def test_retry_worker_fail_and_requeue(mock_send_telegram, mock_sleep, monkeypatch):
    monkeypatch.setattr(message_queue, "config", {"RETRY_LOGIC_TIMEOUT": 1, "RETRY_LOGIC_MAX_ATTEMPTS": 3})
    monkeypatch.setattr(message_queue, "_worker_running", True)
    
    while not message_queue.message_retry_queue.empty():
        message_queue.message_retry_queue.get()
    
    fm = FailedMessage("Fallito temporaneamente")
    message_queue.message_retry_queue.put(fm)
    
    mock_send_telegram.return_value = False 

    try:
        message_queue._retry_worker()
    except InterruptedError:
        pass

    assert fm.attempts == 1
    assert message_queue.message_retry_queue.qsize() == 1
    requeued_item = message_queue.message_retry_queue.get()
    assert requeued_item.attempts == 1

@patch("func.message_queue.time.sleep", side_effect=InterruptedError)
@patch("func.message.send_telegram")
def test_retry_worker_max_attempts_discard(mock_send_telegram, mock_sleep, monkeypatch):
    monkeypatch.setattr(message_queue, "config", {"RETRY_LOGIC_TIMEOUT": 1, "RETRY_LOGIC_MAX_ATTEMPTS": 2})
    monkeypatch.setattr(message_queue, "_worker_running", True)
    
    while not message_queue.message_retry_queue.empty():
        message_queue.message_retry_queue.get()
    
    fm = FailedMessage("Troppi tentativi")
    fm.attempts = 2
    message_queue.message_retry_queue.put(fm)

    try:
        message_queue._retry_worker()
    except InterruptedError:
        pass

    mock_send_telegram.assert_not_called()
    assert message_queue.message_retry_queue.empty()