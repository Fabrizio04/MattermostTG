from func.message import send_telegram
from unittest.mock import patch, MagicMock

def test_send_telegram_missing_credentials(monkeypatch):
    monkeypatch.setattr("func.message.config", {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""})
    
    result = send_telegram("Test message")
    assert result is None

@patch("func.message.requests.post")
def test_send_telegram_success(mock_post, monkeypatch):
    monkeypatch.setattr("func.message.config", {
        "TELEGRAM_BOT_TOKEN": "fake_token",
        "TELEGRAM_CHAT_ID": "fake_chat_id",
        "TG_HTTP_TIMEOUT": 5
    })
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    with patch("func.message.enqueue_failed_message") as mock_enqueue:
        result = send_telegram("Messaggio ok", is_retry=False)
        
        assert result is True
        mock_enqueue.assert_not_called()
        mock_post.assert_called_once_with(
            "https://api.telegram.org/botfake_token/sendMessage",
            json={"chat_id": "fake_chat_id", "text": "Messaggio ok", "parse_mode": "Markdown"},
            timeout=5
        )

@patch("func.message.requests.post")
def test_send_telegram_http_error_not_retry(mock_post, monkeypatch):
    monkeypatch.setattr("func.message.config", {
        "TELEGRAM_BOT_TOKEN": "fake_token",
        "TELEGRAM_CHAT_ID": "fake_chat_id"
    })
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    with patch("func.message.enqueue_failed_message") as mock_enqueue:
        result = send_telegram("Messaggio fallito", is_retry=False)
        
        assert result is False
        mock_enqueue.assert_called_once_with("Messaggio fallito")

@patch("func.message.requests.post")
def test_send_telegram_http_error_is_retry(mock_post, monkeypatch):
    monkeypatch.setattr("func.message.config", {
        "TELEGRAM_BOT_TOKEN": "fake_token",
        "TELEGRAM_CHAT_ID": "fake_chat_id"
    })
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    with patch("func.message.enqueue_failed_message") as mock_enqueue:
        result = send_telegram("Messaggio di retry fallito", is_retry=True)
        
        assert result is False
        mock_enqueue.assert_not_called()

@patch("func.message.requests.post")
def test_send_telegram_exception_enqueues(mock_post, monkeypatch):
    monkeypatch.setattr("func.message.config", {
        "TELEGRAM_BOT_TOKEN": "fake_token",
        "TELEGRAM_CHAT_ID": "fake_chat_id"
    })
    
    mock_post.side_effect = Exception("Connection error")

    with patch("func.message.enqueue_failed_message") as mock_enqueue:
        result = send_telegram("Messaggio in timeout", is_retry=False)
        
        assert result is False
        mock_enqueue.assert_called_once_with("Messaggio in timeout")