from unittest.mock import patch
from func.aes import get_or_create_aes_key, aes, _new_fs_key

def test_new_fs_key(monkeypatch, tmp_path):
    monkeypatch.setattr("func.aes.APP_DIR", str(tmp_path))
    
    key_hex = _new_fs_key()
    assert isinstance(key_hex, str)
    assert len(key_hex) == 64
    
    files = list(tmp_path.glob("*.txt"))
    assert len(files) == 1
    
    key_hex_read = _new_fs_key()
    assert key_hex_read == key_hex

def test_get_or_create_aes_key_headless_with_config(monkeypatch):
    monkeypatch.setenv("HEADLESS", "true")
    
    dummy_key = "a" * 64
    monkeypatch.setattr("func.aes.config", {"AES_ENCRYPTION_KEY": dummy_key})
    
    key = get_or_create_aes_key()
    assert key == dummy_key

def test_get_or_create_aes_key_headless_fallback_fs(monkeypatch, tmp_path):
    monkeypatch.setenv("HEADLESS", "true")
    monkeypatch.setattr("func.aes.config", {})
    monkeypatch.setattr("func.aes.APP_DIR", str(tmp_path))
    
    key = get_or_create_aes_key()
    assert isinstance(key, str)
    assert len(key) == 64

@patch("func.aes.keyring")
def test_get_or_create_aes_key_normal_keyring(mock_keyring, monkeypatch):
    monkeypatch.delenv("HEADLESS", raising=False)
    monkeypatch.setattr("sys.argv", ["script.py"])
    
    mock_keyring.get_password.return_value = "b" * 64
    
    key = get_or_create_aes_key()
    assert key == "b" * 64
    mock_keyring.get_password.assert_called_once()

def test_get_or_create_aes_key():
    key = get_or_create_aes_key()
    
    assert key is not None
    assert isinstance(key, str)
    assert len(key) > 0

def test_aes_disabled(monkeypatch):
    monkeypatch.setattr("func.aes.config", {"AES_ENCRYPTION_ENABLED": False})
    
    result = aes("test-payload")
    assert result == ""

def test_aes_enabled_encryption(monkeypatch, tmp_path):
    monkeypatch.setattr("func.aes.config", {"AES_ENCRYPTION_ENABLED": True})
    monkeypatch.setenv("HEADLESS", "true")
    monkeypatch.setattr("func.aes.APP_DIR", str(tmp_path))
    
    payload = "Messaggio segreto da cifrare"
    result = aes(payload)
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert result != payload