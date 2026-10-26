from unittest.mock import patch, MagicMock
from func.check_on_close import check_on_close

def test_check_on_close_no_changes(monkeypatch):
    monkeypatch.setattr("func.check_on_close.config", {"settings.port": 8080})
    
    parent_mock = MagicMock()
    save_callback_mock = MagicMock()
    
    current_values = {"settings.port": 8080}
    
    result = check_on_close(parent_mock, current_values, save_callback_mock)
    
    assert result is True
    save_callback_mock.assert_not_called()

@patch("ui.CustomMessageBox.CustomMessageBox.ask_save_changes")
def test_check_on_close_with_changes_save(mock_ask_save, monkeypatch):
    monkeypatch.setattr("func.check_on_close.config", {"settings.port": 8080})
    
    parent_mock = MagicMock()
    save_callback_mock = MagicMock()
    mock_ask_save.return_value = "save"
    
    current_values = {"settings.port": 9090}
    result = check_on_close(parent_mock, current_values, save_callback_mock)
    
    assert result is True
    save_callback_mock.assert_called_once()
    mock_ask_save.assert_called_once()

@patch("ui.CustomMessageBox.CustomMessageBox.ask_save_changes")
def test_check_on_close_with_changes_discard(mock_ask_save, monkeypatch):
    monkeypatch.setattr("func.check_on_close.config", {"settings.port": 8080})
    
    parent_mock = MagicMock()
    save_callback_mock = MagicMock()
    mock_ask_save.return_value = "discard"
    
    current_values = {"settings.port": 9090}
    result = check_on_close(parent_mock, current_values, save_callback_mock)
    
    assert result is True
    save_callback_mock.assert_not_called()

@patch("ui.CustomMessageBox.CustomMessageBox.ask_save_changes")
def test_check_on_close_with_changes_cancel(mock_ask_save, monkeypatch):
    monkeypatch.setattr("func.check_on_close.config", {"settings.port": 8080})
    
    parent_mock = MagicMock()
    save_callback_mock = MagicMock()
    mock_ask_save.return_value = "cancel"
    
    current_values = {"settings.port": 9090}
    result = check_on_close(parent_mock, current_values, save_callback_mock)
    
    assert result is False
    save_callback_mock.assert_not_called()