import json
import pytest
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

def test_handle_imported_sensitive_data(tmp_path):
    config_file = tmp_path / "config.json"
    initial_data = {
        "MATTERMOST_WS_URL": "wss://test.com",
        "MATTERMOST_TOKEN": "secret_mm_token_123",
        "TELEGRAM_BOT_TOKEN": "secret_tg_token_456",
        "AES_ENCRYPTION_KEY": "secret_aes_key_789",
        "THEME": "light"
    }
    config_file.write_text(json.dumps(initial_data), encoding="utf-8")

    with patch("settings.CONFIG_FILE_PATH", str(config_file)), \
         patch("settings.keyring.set_password") as mock_set_password:
        
        settings.handle_imported_sensitive_data()

        assert mock_set_password.call_count == 3
        mock_set_password.assert_any_call("MattermostNotifier", "MATTERMOST_TOKEN", "secret_mm_token_123")
        mock_set_password.assert_any_call("MattermostNotifier", "TELEGRAM_BOT_TOKEN", "secret_tg_token_456")
        mock_set_password.assert_any_call("MattermostNotifier", "AES_ENCRYPTION_KEY", "secret_aes_key_789")

    with open(config_file, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    assert "MATTERMOST_TOKEN" not in updated_data
    assert "TELEGRAM_BOT_TOKEN" not in updated_data
    assert "AES_ENCRYPTION_KEY" not in updated_data
    assert updated_data["MATTERMOST_WS_URL"] == "wss://test.com"
    assert updated_data["THEME"] == "light"

def test_validate_config_valid_cases():
    valid_configs = [
        {},
        {"THEME": "light", "LOG_LEVEL": "DEBUG"},
        {"MATTERMOST_WS_URL": "wss://test.mattermost.com", "WS_RECONNECT_TIMEOUT": 10},
        {"TELEGRAM_CHAT_ID": 12345678, "ANONYMOUS_MODE": True, "LANGUAGE": "it_IT"},
        {"MATTERMOST_TOKEN": "secret_token_123"}
    ]
    for cfg in valid_configs:
        assert settings.validate_config(cfg) is True

def test_validate_config_non_dict_input():
    assert settings.validate_config(None) is False
    assert settings.validate_config("not_a_dict") is False
    assert settings.validate_config([1, 2, 3]) is False

def test_validate_config_unknown_keys():
    assert settings.validate_config({"CHIAVE_SCONOSCIUTA": "valore"}) is False

@pytest.mark.parametrize("key,value", [
    ("MATTERMOST_WS_URL", "http://not-a-websocket.com"),  # URL non ws:// o wss://
    ("WS_RECONNECT_TIMEOUT", "10"),                       # Stringa anziché intero
    ("RETRY_LOGIC_TIMEOUT", 15.5),                        # Float anziché intero
    ("ECHO_SUPPRESSION_ENABLED", "True"),                 # Stringa anziché booleano
    ("LOG_LEVEL", "SUPER_DEBUG"),                         # Log level inesistente
    ("THEME", "neon"),                                    # Tema inesistente
    ("LANGUAGE", "en-US"),                                # Formato BCP 47 errato (deve essere underscore it_IT)
    ("LANGUAGE", "italiano"),                             # Formato errato
    ("LANGUAGE", 123),                                    # Tipo errato per la lingua
    ("TELEGRAM_CHAT_ID", [12345]),                        # Lista non ammessa per il chat ID
    ("EXCLUDED_SENDERS", 999),                            # Intero anziché stringa
])
def test_validate_config_invalid_values(key, value):
    config_to_test = {key: value}
    assert settings.validate_config(config_to_test) is False

def test_reset_settings():
    with patch("settings.get_system_locale", return_value="it"):
        settings.reset_settings()
        assert settings.config["MATTERMOST_WS_URL"] == ""
        assert settings.config["THEME"] == "light"
        assert settings.config["ECHO_SUPPRESSION_ENABLED"] is True