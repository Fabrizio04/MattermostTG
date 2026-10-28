import json
import settings

from unittest.mock import patch, MagicMock

def test_load_settings_file_exists(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"MATTERMOST_WS_URL": "wss://test.com", "THEME": "dark"}), encoding="utf-8")

    with patch("settings.CONFIG_FILE_PATH", str(cfg_file)), \
         patch("keyring.get_password", return_value=None):
        
        settings.load_settings()
        assert settings.config["MATTERMOST_WS_URL"] == "wss://test.com"
        assert settings.config["THEME"] == "dark"

def test_load_settings_headless_mode():
    args = MagicMock()
    args.headless = True
    args.config = ""
    args.ws_url = "wss://headless.com"
    args.token = "mm_token_123"
    args.bot_token = "tg_token_456"
    args.chat_id = "chat_789"
    args.excluded_senders = ""
    args.excluded_channels = ""
    args.echo_suppression = True
    args.anonymous_mode = False
    args.include_sender = True
    args.include_channel = True
    args.include_message = True
    args.aes_enabled = False
    args.aes_key = "aes_key_abc"
    args.ws_val = 5
    args.retry_val = 10
    args.attempts_val = 5
    args.tg_http_val = 5
    args.log_level = "INFO"
    args.lang = "it"
    args.port = 8080
    args.http_user = "admin"
    args.http_pass = "password"

    settings.load_settings(args)
    assert settings.config["MATTERMOST_WS_URL"] == "wss://headless.com"
    assert settings.config["MATTERMOST_TOKEN"] == "mm_token_123"
    assert settings.config["PORT"] == 8080

def test_load_settings_headless_custom_config(tmp_path):
    cfg_file = tmp_path / "custom_config.json"
    cfg_file.write_text(json.dumps({"MATTERMOST_WS_URL": "wss://custom.com"}), encoding="utf-8")

    args = MagicMock()
    args.headless = True
    args.config = str(cfg_file)

    settings.load_settings(args)
    assert settings.config["MATTERMOST_WS_URL"] == "wss://custom.com"

def test_save_settings(tmp_path):
    cfg_file = tmp_path / "config.json"

    with patch("settings.CONFIG_FILE_PATH", str(cfg_file)), \
         patch("keyring.set_password") as mock_set_key:
        
        settings.save_settings(
            ws_url="wss://save.com",
            mm_token="mm_t",
            tg_token="tg_t",
            tg_chat_id="12345",
            excluded_senders="user1",
            excluded_channels="chan1",
            echo_suppression=True,
            anonymous_mode=False,
            include_sender=True,
            include_channel=True,
            include_message=True,
            aes_enabled=False,
            always_on_top=False,
            ws_val=5,
            retry_val=10,
            attempts_val=5,
            tg_http_val=5,
            log_level="INFO",
            theme="dark",
            lang="en"
        )

        assert cfg_file.exists()
        saved_data = json.loads(cfg_file.read_text(encoding="utf-8"))
        assert saved_data["MATTERMOST_WS_URL"] == "wss://save.com"
        assert saved_data["THEME"] == "dark"
        assert mock_set_key.call_count == 2

def test_reset_settings():
    with patch("settings.get_system_locale", return_value="it"):
        settings.reset_settings()
        assert settings.config["MATTERMOST_WS_URL"] == ""
        assert settings.config["THEME"] == "light"
        assert settings.config["ECHO_SUPPRESSION_ENABLED"] is True