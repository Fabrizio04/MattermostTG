from unittest.mock import patch
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QCloseEvent
from ui.TimeoutSettingsDialog import TimeoutSettingsDialog

def test_timeout_settings_dialog_init(qtbot, monkeypatch):
    monkeypatch.setattr("ui.TimeoutSettingsDialog.config", {
        "THEME": "light",
        "WS_RECONNECT_TIMEOUT": 5,
        "RETRY_LOGIC_TIMEOUT": 10,
        "RETRY_LOGIC_MAX_ATTEMPTS": 5,
        "TG_HTTP_TIMEOUT": 5
    })

    with patch("ui.TimeoutSettingsDialog.check_on_close", return_value=True), \
         patch("ui.TimeoutSettingsDialog.get", side_effect=lambda k: k):
        
        dlg = TimeoutSettingsDialog()
        
        assert dlg.ws_timeout_spin.value() == 5
        assert dlg.retry_timeout_spin.value() == 10
        assert dlg.max_attempts_spin.value() == 5
        assert dlg.timeout_http_tg.value() == 5

        dlg.close()

def test_timeout_settings_dialog_save(qtbot, monkeypatch):
    monkeypatch.setattr("ui.TimeoutSettingsDialog.config", {
        "THEME": "light",
        "WS_RECONNECT_TIMEOUT": 5,
        "RETRY_LOGIC_TIMEOUT": 10,
        "RETRY_LOGIC_MAX_ATTEMPTS": 5,
        "TG_HTTP_TIMEOUT": 5
    })

    with patch("ui.TimeoutSettingsDialog.check_on_close", return_value=True), \
         patch("ui.TimeoutSettingsDialog.save_settings") as mock_save, \
         patch("ui.TimeoutSettingsDialog.CustomMessageBox.show_info") as mock_show_info, \
         patch("ui.TimeoutSettingsDialog.get", side_effect=lambda k: k):
        
        dlg = TimeoutSettingsDialog()
        
        dlg.ws_timeout_spin.setValue(15)
        
        dlg.save_settings(showMessage=True)
        
        mock_save.assert_called_once()
        mock_show_info.assert_called_once()

        dlg.close()

def test_timeout_settings_dialog_close_cancelled(qtbot, monkeypatch):
    monkeypatch.setattr("ui.TimeoutSettingsDialog.config", {
        "THEME": "light",
        "WS_RECONNECT_TIMEOUT": 5,
        "RETRY_LOGIC_TIMEOUT": 10,
        "RETRY_LOGIC_MAX_ATTEMPTS": 5,
        "TG_HTTP_TIMEOUT": 5
    })

    with patch("ui.TimeoutSettingsDialog.check_on_close", return_value=False), \
         patch("ui.TimeoutSettingsDialog.get", side_effect=lambda k: k):
        
        dlg = TimeoutSettingsDialog()
        
        event = QCloseEvent()
        dlg.closeEvent(event)
        
        assert not event.isAccepted()

@patch("ui.TimeoutSettingsDialog.exec_with_parent_dim")
def test_open_timeout_settings_dialog_static(mock_exec_dim, qtbot, monkeypatch):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    monkeypatch.setattr("ui.TimeoutSettingsDialog.config", {
        "THEME": "light",
        "WS_RECONNECT_TIMEOUT": 5,
        "RETRY_LOGIC_TIMEOUT": 10,
        "RETRY_LOGIC_MAX_ATTEMPTS": 5,
        "TG_HTTP_TIMEOUT": 5
    })
    
    with patch("ui.TimeoutSettingsDialog.check_on_close", return_value=True), \
         patch("ui.TimeoutSettingsDialog.get", side_effect=lambda k: k):
        
        TimeoutSettingsDialog.open_TimeoutSettingsDialog(parent=parent)
        
    mock_exec_dim.assert_called_once()
    args, _ = mock_exec_dim.call_args
    assert isinstance(args[0], TimeoutSettingsDialog)
    assert args[1] == parent