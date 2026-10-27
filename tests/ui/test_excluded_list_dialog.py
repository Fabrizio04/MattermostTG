from unittest.mock import patch
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QCloseEvent

from ui.ExcludedListDialog import ExcludedListDialog

def test_excluded_list_dialog_init_senders(qtbot, monkeypatch):
    monkeypatch.setattr("ui.ExcludedListDialog.config", {"EXCLUDED_SENDERS": "user1, user2"})
    
    with patch("ui.ExcludedListDialog.check_on_close", return_value=True), \
         patch("ui.ExcludedListDialog.get", side_effect=lambda k: k):
        dlg = ExcludedListDialog(list_type="senders")
        # qtbot.addWidget(dlg)
        
        assert dlg.list_type == "senders"
        assert dlg.config_key == "EXCLUDED_SENDERS"
        assert dlg.text_area.toPlainText() == "user1, user2"

        dlg.close()

def test_excluded_list_dialog_init_channels(qtbot, monkeypatch):
    monkeypatch.setattr("ui.ExcludedListDialog.config", {"EXCLUDED_CHANNELS": "general, random"})
    
    with patch("ui.ExcludedListDialog.check_on_close", return_value=True), \
         patch("ui.ExcludedListDialog.get", side_effect=lambda k: k):
        dlg = ExcludedListDialog(list_type="channels")
        # qtbot.addWidget(dlg)
        
        assert dlg.list_type == "channels"
        assert dlg.config_key == "EXCLUDED_CHANNELS"
        assert dlg.text_area.toPlainText() == "general, random"

        dlg.close()

def test_excluded_list_dialog_save(qtbot, monkeypatch):
    monkeypatch.setattr("ui.ExcludedListDialog.config", {"EXCLUDED_SENDERS": ""})

    with patch("ui.ExcludedListDialog.check_on_close", return_value=True), \
         patch("ui.ExcludedListDialog.get", side_effect=lambda k: k), \
         patch("ui.ExcludedListDialog.save_settings") as mock_save_settings, \
         patch("ui.ExcludedListDialog.CustomMessageBox.show_info") as mock_show_info:
        
        dlg = ExcludedListDialog(list_type="senders")
        # qtbot.addWidget(dlg)
        
        dlg.text_area.setPlainText("new_user")
        
        dlg.save_list(showMessage=True)
        
        mock_save_settings.assert_called_once()
        mock_show_info.assert_called_once()

        dlg.close()

def test_excluded_list_dialog_close_cancelled(qtbot, monkeypatch):
    monkeypatch.setattr("ui.ExcludedListDialog.config", {"EXCLUDED_SENDERS": "user1"})

    with patch("ui.ExcludedListDialog.check_on_close", return_value=False), \
         patch("ui.ExcludedListDialog.get", side_effect=lambda k: k):
        
        dlg = ExcludedListDialog(list_type="senders")
        
        dlg.text_area.setPlainText("user1, user_modificato")
        
        event = QCloseEvent()
        dlg.closeEvent(event)
        
        assert not event.isAccepted()

        dlg.close()

@patch("ui.ExcludedListDialog.exec_with_parent_dim")
def test_open_excluded_list_dialog_static(mock_exec_dim, qtbot, monkeypatch):
    parent_widget = QWidget()
    qtbot.addWidget(parent_widget)
    
    monkeypatch.setattr("ui.ExcludedListDialog.config", {"EXCLUDED_SENDERS": ""})
    
    with patch("ui.ExcludedListDialog.check_on_close", return_value=True), \
         patch("ui.ExcludedListDialog.get", side_effect=lambda k: k):
        
        ExcludedListDialog.open_ExcludedListDialog(list_type="senders", parent=parent_widget)
        
    mock_exec_dim.assert_called_once()
    args, _ = mock_exec_dim.call_args
    assert isinstance(args[0], ExcludedListDialog)
    assert args[1] == parent_widget