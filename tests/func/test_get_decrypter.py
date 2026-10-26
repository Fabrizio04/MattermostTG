from unittest.mock import patch
from func.decrypter import get_decrypter

def test_get_decrypter_file_not_found(monkeypatch, tmp_path):
    monkeypatch.setattr("func.decrypter.resource_path", lambda path: str(tmp_path / "non_existent.html"))
    
    result = get_decrypter(includeKey=False)
    assert result == "NF"

def test_get_decrypter_success_without_key(tmp_path, monkeypatch):
    web_dir = tmp_path / "web"
    web_dir.mkdir()
    html_file = web_dir / "decrypter.html"
    html_file.write_text("Key: ===KEY===, Private: ===MY_PRIVATE_KEY===, Upload: ===UPLOAD===", encoding="utf-8")
    
    monkeypatch.setattr("func.decrypter.resource_path", lambda path: str(html_file))
    
    with patch("func.decrypter.get", side_effect=lambda key, **kwargs: f"val_{key}"):
        result = get_decrypter(includeKey=False)
        
        assert "Key: val_decrypter.key" in result
        assert "Private: " in result
        assert "Upload: val_decrypter.upload" in result

def test_get_decrypter_success_with_key(tmp_path, monkeypatch):
    web_dir = tmp_path / "web"
    web_dir.mkdir()
    html_file = web_dir / "decrypter.html"
    html_file.write_text("Private: ===MY_PRIVATE_KEY===", encoding="utf-8")
    
    monkeypatch.setattr("func.decrypter.resource_path", lambda path: str(html_file))
    
    with patch("func.decrypter.get", side_effect=lambda key, **kwargs: f"val_{key}"), \
         patch("func.decrypter.get_or_create_aes_key", return_value="FAKE_AES_KEY_12345"):
         
        result = get_decrypter(includeKey=True)
        assert "Private: FAKE_AES_KEY_12345" in result

def test_get_decrypter_exception(monkeypatch, tmp_path):
    invalid_path_target = tmp_path / "decrypter.html"
    invalid_path_target.mkdir()
    
    monkeypatch.setattr("func.decrypter.resource_path", lambda path: str(invalid_path_target))
    
    result = get_decrypter(includeKey=False)
    assert result == ""