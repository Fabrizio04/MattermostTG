from unittest.mock import patch
from func.format_notification import format_notification

def test_format_notification_standard(monkeypatch):
    monkeypatch.setattr("func.format_notification.config", {
        "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True,
        "INCLUDE_SENDER": True,
        "INCLUDE_MESSAGE": True,
        "AES_ENCRYPTION_ENABLED": False
    })
    
    def mock_get(key_path, default=None):
        mapping = {
            "main.date_format": "%Y-%m-%d %H:%M:%S",
            "main.date": "Data",
            "main.channel": "Canale",
            "main.sender": "Mittente",
            "main.message": "Messaggio"
        }
        return mapping.get(key_path, key_path)

    monkeypatch.setattr("func.format_notification.get", mock_get)
    
    res = format_notification(1600000000000, "general", "Mario", "Ciao a tutti")
    
    assert "Mattermost Notifier" in res
    assert "Data:* 2020-09-13" in res
    assert "Canale:* general" in res
    assert "Mittente:* Mario" in res
    assert "Messaggio:*\nCiao a tutti" in res

def test_format_notification_anonymous_mode(monkeypatch):
    monkeypatch.setattr("func.format_notification.config", {
        "ANONYMOUS_MODE": True,
        "AES_ENCRYPTION_ENABLED": False
    })
    
    def mock_get(key_path, default=None):
        mapping = {
            "main.date_format": "%Y-%m-%d",
            "main.date": "Data",
            "main.default_msg": "Messaggio privato standard"
        }
        return mapping.get(key_path, key_path)

    monkeypatch.setattr("func.format_notification.get", mock_get)
    
    res = format_notification(1600000000000, "general", "Mario", "Segreto")

    assert "Data:* 2020-09-13" in res
    assert "Messaggio privato standard" in res
    assert "general" not in res
    assert "Mario" not in res
    assert "Segreto" not in res

@patch("func.format_notification.aes")
def test_format_notification_with_aes_encryption(mock_aes, monkeypatch):
    monkeypatch.setattr("func.format_notification.config", {
        "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": False,
        "INCLUDE_SENDER": False,
        "INCLUDE_MESSAGE": True,
        "AES_ENCRYPTION_ENABLED": True
    })
    
    def mock_get(key_path, default=None):
        return "%Y-%m-%d"
        
    monkeypatch.setattr("func.format_notification.get", mock_get)
    mock_aes.return_value = "CIPHERTEXT_ABC123"
    
    res = format_notification(None, "general", "Mario", "Messaggio da cifrare")
    
    mock_aes.assert_called_once()
    assert res == "CIPHERTEXT_ABC123"

def test_format_notification_with_emojis(monkeypatch):
    monkeypatch.setattr("func.format_notification.config", {
        "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": False,
        "INCLUDE_SENDER": False,
        "INCLUDE_MESSAGE": True,
        "AES_ENCRYPTION_ENABLED": False
    })

    def mock_get(key_path, default=None):
        mapping = {
            "main.date_format": "%Y-%m-%d",
            "main.date": "Data",
            "main.message": "Messaggio"
        }
        return mapping.get(key_path, key_path)

    monkeypatch.setattr("func.format_notification.get", mock_get)
    res = format_notification(1600000000000, "general", "Mario", "Ciao :smile: e :test:")

    assert "😄" in res
    assert "[[test]]" in res