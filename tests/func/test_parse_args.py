import sys
import pytest
from unittest.mock import patch
from func.parse_args import parse_args

def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script.py"])
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("HEADLESS", raising=False)
    
    with patch("func.parse_args.get", side_effect=lambda key, default=None: key), \
         patch("func.parse_args.get_system_locale", return_value="en_US"):
         
        args = parse_args()
        
        assert args.port == 8080
        assert args.headless is False
        assert args.open_settings is False
        assert args.lang == "en_US"
        assert args.http_user == ""

def test_parse_args_custom_values(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "script.py",
        "--port", "9090",
        "--headless",
        "--http-user", "admin_user",
        "--lang", "it_IT",
        "--aes-enabled"
    ])
    
    with patch("func.parse_args.get", side_effect=lambda key, default=None: key):
        args = parse_args()
        
        assert args.port == 9090
        assert args.headless is True
        assert args.http_user == "admin_user"
        assert args.lang == "it_IT"
        assert args.aes_enabled is True

def test_parse_args_windows_help_slash(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script.py", "/?"])
    
    with patch("func.parse_args.get", side_effect=lambda key, default=None: key):
        with pytest.raises(SystemExit):
            parse_args()