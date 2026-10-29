import pytest

from pathlib import Path
from PyQt6.QtCore import Qt
from unittest.mock import patch, MagicMock
from ui.SettingsDialog import SettingsDialog


def test_settings_dialog_init(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "wss://test.mattermost.com",
        "MATTERMOST_TOKEN": "token123",
        "TELEGRAM_BOT_TOKEN": "bot_token_abc",
        "TELEGRAM_CHAT_ID": "123456789",
        "AES_ENCRYPTION_ENABLED": False,
        "ECHO_SUPPRESSION_ENABLED": True,
        "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True,
        "INCLUDE_SENDER": True,
        "INCLUDE_MESSAGE": True,
        "ALWAYS_ON_TOP": False,
        "THEME": "light",
        "LANGUAGE": "it"
    })
    
    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        assert dlg.txt_ws_url.text() == "wss://test.mattermost.com"
        assert dlg.txt_mm_token.text() == "token123"
        assert dlg.txt_tg_token.text() == "bot_token_abc"
        assert dlg.txt_tg_chat_id.text() == "123456789"
        assert dlg.toggle_aes.isChecked() is False
        assert dlg.toggle_anon.isChecked() is False
        assert dlg.toggle_channel.isChecked() is True
        
        dlg.close()

def test_settings_dialog_update_ui(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k: f"translated_{k}"), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False), \
         patch("mattermost_listener.is_websocket_connected", return_value=True):
        
        dlg = SettingsDialog()
        # qtbot.addWidget(dlg)
        
        dlg.update_ui()
        
        assert dlg.btn_save.text() == "translated_settings.ui.btn_save"
        assert dlg.group_granular.title() == "translated_settings.ui.group_granular"
        
        dlg.close()

@patch("subprocess.Popen")
@patch("os.startfile", create=True)
def test_settings_dialog_open_app_path_folder(mock_startfile, mock_popen, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.open_app_path_folder()
        
        dlg.close()

def test_settings_dialog_export_settings_json(qtbot, monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"THEME": "light"}', encoding="utf-8")
    
    export_target = tmp_path / "exported_config.json"

    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.CONFIG_FILE_PATH", str(config_file)), \
         patch("ui.SettingsDialog.QFileDialog.getSaveFileName", return_value=(str(export_target), "JSON Files (*.json)")), \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.get", side_effect=lambda k: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.export_settings_json()
        
        assert export_target.exists()
        assert export_target.read_text(encoding="utf-8") == '{"THEME": "light"}'
        mock_info.assert_called_once()
        
        dlg.close()

def test_settings_dialog_import_settings_json(qtbot, monkeypatch, tmp_path):
    import_source = tmp_path / "import_config.json"
    import_source.write_text('{"MATTERMOST_WS_URL": "wss://imported.com"}', encoding="utf-8")
    
    config_target = tmp_path / "sub" / "config.json"
    config_target.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    def mock_get(key, default=None, *args, **kwargs):
        if isinstance(default, bool):
            return True
        return key

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.CONFIG_FILE_PATH", str(config_target)), \
         patch("ui.SettingsDialog.QFileDialog.getOpenFileName", return_value=(str(import_source), "JSON Files (*.json)")), \
         patch("settings.load_settings") as mock_load_settings, \
         patch("mattermost_listener.reconnect_websocket") as mock_reconnect, \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.CustomMessageBox.show_critical") as mock_crit, \
         patch("ui.SettingsDialog.get", side_effect=mock_get), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.import_settings_json()
        
        if mock_crit.called:
            print("CRITICAL CALLED WITH:", mock_crit.call_args)
        
        assert config_target.exists()
        mock_load_settings.assert_called_once()
        mock_reconnect.assert_called_once()
        mock_info.assert_called_once()
        mock_crit.assert_not_called()
        
        dlg.close()

def test_settings_dialog_regenerate_aes_key(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.CustomMessageBox.ask_yes_no", return_value="yes"), \
         patch("ui.SettingsDialog.keyring.delete_password") as mock_delete, \
         patch("ui.SettingsDialog.get_or_create_aes_key") as mock_get_key, \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.regenerate_aes_key()
        
        mock_delete.assert_called_once()
        mock_get_key.assert_called_once()
        mock_info.assert_called_once()
        
        dlg.close()

def test_settings_dialog_download_raw_key(qtbot, monkeypatch, tmp_path):
    key_file = tmp_path / "aes_key.txt"

    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get_or_create_aes_key", return_value="mock_secret_aes_key_123"), \
         patch("ui.SettingsDialog.QFileDialog.getSaveFileName", return_value=(str(key_file), "Text Files (*.txt)")), \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.download_raw_key()
        
        assert key_file.exists()
        assert key_file.read_text(encoding="utf-8") == "mock_secret_aes_key_123"
        mock_info.assert_called_once()
        
        dlg.close()

def test_settings_dialog_toggle_anonymous_mode(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.toggle_anonymous_mode(True)
        assert dlg.group_granular.isEnabled() is False
        
        dlg.toggle_anonymous_mode(False)
        assert dlg.group_granular.isEnabled() is True
        
        dlg.close()

def test_settings_dialog_download_decrypter_html(qtbot, monkeypatch, tmp_path):
    html_file = tmp_path / "decrypter.html"

    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get_decrypter", return_value="<html>Mock Decrypter</html>"), \
         patch("ui.SettingsDialog.QFileDialog.getSaveFileName", return_value=(str(html_file), "File HTML (*.html)")), \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.download_decrypter_html(True)
        
        assert html_file.exists()
        assert html_file.read_text(encoding="utf-8") == "<html>Mock Decrypter</html>"
        mock_info.assert_called_once()
        
        dlg.close()

def test_settings_dialog_notifications_menu(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.controller = MagicMock()
        
        dlg.toggle_notifications_from_menu(True)
        dlg.controller.toggle_service.assert_called_once_with(True)
        
        dlg.update_menu_toggle_notification(False)
        assert dlg.act_notif.isChecked() is False
        
        dlg.close()

def test_settings_dialog_update_on_top_window(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.save = MagicMock()
        
        dlg.update_on_top_window(True, save=False)
        assert dlg.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        
        dlg.update_on_top_window(False, save=False)
        assert not (dlg.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        
        dlg.close()

def test_settings_dialog_open_excluded_dialog(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.ExcludedListDialog.open_ExcludedListDialog") as mock_open_exc, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.open_excluded_dialog("senders")
        mock_open_exc.assert_called_once_with("senders", dlg)
        
        dlg.close()

@pytest.mark.parametrize("platform_name, checked", [
    ("win32", True),
    ("win32", False),
    ("linux", True),
    ("linux", False),
    ("darwin", True),
    ("darwin", False),
])
def test_settings_dialog_set_auto_startup_parametrized(qtbot, monkeypatch, tmp_path, platform_name, checked):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    mock_winreg = MagicMock()
    
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("sys.platform", platform_name), \
         patch.dict("sys.modules", {"winreg": mock_winreg}), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.set_auto_startup(checked)
        
        if platform_name.startswith("win"):
            if checked:
                mock_winreg.OpenKey.assert_called_once()
                mock_winreg.SetValueEx.assert_called_once()
            else:
                mock_winreg.DeleteValue.assert_called_once()
        elif platform_name.startswith("linux"):
            desktop_file = tmp_path / ".config" / "autostart" / "mattermost_notifier.desktop"
            if checked:
                assert desktop_file.exists()
                assert "Desktop Entry" in desktop_file.read_text(encoding="utf-8")
            else:
                assert not desktop_file.exists()
        elif platform_name.startswith("darwin"):
            plist_file = tmp_path / "Library" / "LaunchAgents" / "com.mattermost.notifier.plist"
            if checked:
                assert plist_file.exists()
                assert "com.mattermost.notifier" in plist_file.read_text(encoding="utf-8")
            else:
                assert not plist_file.exists()
        
        dlg.close()

def test_settings_dialog_open_timeout_settings(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.TimeoutSettingsDialog.open_TimeoutSettingsDialog") as mock_timeout, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.open_timeout_settings()
        mock_timeout.assert_called_once_with(dlg)
        dlg.close()

def test_settings_dialog_open_log(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.LogViewerDialog") as mock_log_cls, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.open_log()
        mock_log_cls.assert_called_once()
        
        dlg.log_dialog.isVisible = lambda: True
        dlg.log_dialog.activateWindow = MagicMock()
        dlg.log_dialog.raise_ = MagicMock()
        
        dlg.open_log()
        dlg.log_dialog.activateWindow.assert_called_once()
        
        dlg.close()

@patch("ui.SettingsDialog.check_for_updates")
@patch("ui.SettingsDialog.CustomMessageBox")
@patch("ui.SettingsDialog.webbrowser")
def test_check_update_available_yes(mock_webbrowser, mock_msg_box, mock_check_updates, qapp):
    mock_check_updates.return_value = (True, "1.2.0", "https://github.com/Fabrizio04/MattermostTG/releases/tag/v1.2.0")
    mock_msg_box.ask_yes_no.return_value = "yes"
    
    dialog = SettingsDialog(qapp)
    dialog.check_update()
    
    mock_msg_box.ask_yes_no.assert_called_once()
    mock_webbrowser.open.assert_called_once_with("https://github.com/Fabrizio04/MattermostTG/releases/tag/v1.2.0")

@patch("ui.SettingsDialog.check_for_updates")
@patch("ui.SettingsDialog.CustomMessageBox")
@patch("ui.SettingsDialog.webbrowser")
def test_check_update_available_no(mock_webbrowser, mock_msg_box, mock_check_updates, qapp):
    mock_check_updates.return_value = (True, "1.2.0", "https://github.com/Fabrizio04/MattermostTG/releases/tag/v1.2.0")
    mock_msg_box.ask_yes_no.return_value = "no"
    
    dialog = SettingsDialog(qapp)
    dialog.check_update()
    
    mock_msg_box.ask_yes_no.assert_called_once()
    mock_webbrowser.open.assert_not_called()

@patch("ui.SettingsDialog.check_for_updates")
@patch("ui.SettingsDialog.CustomMessageBox")
def test_check_update_not_available(mock_msg_box, mock_check_updates, qapp):
    mock_check_updates.return_value = (False, "1.0.0", "")
    
    dialog = SettingsDialog(qapp)
    dialog.check_update()
    
    mock_msg_box.show_info.assert_called_once()

def test_settings_dialog_open_about(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.AboutDialog.open_AboutDialog") as mock_about, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.open_about()
        mock_about.assert_called_once_with(dlg)
        dlg.close()

def test_settings_dialog_reset_settings(qtbot, monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"THEME": "light"}', encoding="utf-8")

    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.CONFIG_FILE_PATH", str(config_file)), \
         patch("ui.SettingsDialog.CustomMessageBox.ask_yes_no", return_value="yes"), \
         patch("ui.SettingsDialog.reset_settings") as mock_reset_func, \
         patch("mattermost_listener.reconnect_websocket") as mock_reconnect, \
         patch("ui.SettingsDialog.load_language") as mock_load_lang, \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.controller = MagicMock()
        
        dlg.reset_settings()
        
        mock_reset_func.assert_called_once()
        mock_reconnect.assert_called_once()
        mock_load_lang.assert_called_once()
        mock_info.assert_called_once()
        
        dlg.close()

def test_settings_dialog_update_theme(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.save_settings") as mock_save_settings, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.controller = MagicMock()
        
        dlg.update_theme()
        
        mock_save_settings.assert_called_once()
        dlg.controller.on_save_settings.assert_called_once()
        
        dlg.close()

def test_settings_dialog_save(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.save_settings") as mock_save_settings, \
         patch("mattermost_listener.reconnect_websocket") as mock_reconnect, \
         patch("ui.SettingsDialog.CustomMessageBox.show_info") as mock_info, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.save(showMessage=True)
        mock_save_settings.assert_called_once()
        mock_reconnect.assert_called_once()
        mock_info.assert_called_once()
        
        mock_reconnect.reset_mock()
        mock_info.reset_mock()
        dlg.save(showMessage=False)
        mock_reconnect.assert_not_called()
        mock_info.assert_not_called()
        
        dlg.close()

def test_settings_dialog_update_service_indicator_ui(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.update_service_indicator_ui(True)
        assert "#00b4d8" in dlg.service_indicator.styleSheet()
        
        dlg.update_service_indicator_ui(False)
        assert "#adb5bd" in dlg.service_indicator.styleSheet()
        
        dlg.close()

def test_settings_dialog_update_ws_indicator_ui(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        
        dlg.update_ws_indicator_ui(True)
        assert "#009933" in dlg.ws_indicator.styleSheet()
        
        dlg.update_ws_indicator_ui(False)
        assert "#e63946" in dlg.ws_indicator.styleSheet()
        
        dlg.close()

def test_settings_dialog_close_event(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    mock_event = MagicMock()

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.closeEvent(mock_event)
        mock_event.accept.assert_called_once()
        dlg.close()

    mock_event.reset_mock()
    with patch("ui.SettingsDialog.check_on_close", return_value=False), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.closeEvent(mock_event)
        mock_event.ignore.assert_called_once()
        dlg.close()

def test_settings_dialog_reject(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.close = MagicMock()
        
        dlg.reject()
        dlg.close.assert_called_once()
        
        dlg.close()

def test_settings_dialog_update_language(qtbot, monkeypatch):
    monkeypatch.setattr("ui.SettingsDialog.config", {
        "MATTERMOST_WS_URL": "", "MATTERMOST_TOKEN": "", "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": "",
        "AES_ENCRYPTION_ENABLED": False, "ECHO_SUPPRESSION_ENABLED": True, "ANONYMOUS_MODE": False,
        "INCLUDE_CHANNEL": True, "INCLUDE_SENDER": True, "INCLUDE_MESSAGE": True, "ALWAYS_ON_TOP": False,
        "THEME": "light", "LANGUAGE": "it"
    })

    with patch("ui.SettingsDialog.check_on_close", return_value=True), \
         patch("ui.SettingsDialog.LanguageDialog.open_LanguageDialog") as mock_lang_dlg, \
         patch("ui.SettingsDialog.get", side_effect=lambda k, *args: k), \
         patch("ui.SettingsDialog.check_auto_startup", return_value=False):
        
        dlg = SettingsDialog()
        dlg.update_language()
        mock_lang_dlg.assert_called_once_with(dlg)
        dlg.close()