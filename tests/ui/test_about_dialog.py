from unittest.mock import patch
from PyQt6.QtWidgets import QPushButton, QWidget

from ui.AboutDialog import AboutDialog

def test_about_dialog_light_theme(qtbot, monkeypatch):
    monkeypatch.setattr("ui.AboutDialog.config", {"THEME": "light"})
    
    with patch("ui.AboutDialog.get", side_effect=lambda k: k):
        dlg = AboutDialog()
        qtbot.addWidget(dlg)
        
        assert dlg.width() == 380
        assert dlg.height() == 280
        
        close_btn = dlg.findChild(QPushButton)
        assert close_btn is not None

def test_about_dialog_dark_theme(qtbot, monkeypatch):
    monkeypatch.setattr("ui.AboutDialog.config", {"THEME": "dark"})
    
    with patch("ui.AboutDialog.get", side_effect=lambda k: k):
        dlg = AboutDialog()
        qtbot.addWidget(dlg)
        
        assert dlg.isVisible() is False

def test_about_dialog_close_button(qtbot):
    with patch("ui.AboutDialog.get", side_effect=lambda k: k), \
         patch.object(AboutDialog, "accept") as mock_accept:
        
        dlg = AboutDialog()
        qtbot.addWidget(dlg)
        close_btn = dlg.findChild(QPushButton)
        
        close_btn.click()
        mock_accept.assert_called_once()

@patch("ui.AboutDialog.exec_with_parent_dim")
def test_open_about_dialog_static(mock_exec_dim, qtbot):
    parent_widget = QWidget()
    qtbot.addWidget(parent_widget)
    
    with patch("ui.AboutDialog.get", side_effect=lambda k: k):
        AboutDialog.open_AboutDialog(parent_widget)
    
    mock_exec_dim.assert_called_once()
    args, _ = mock_exec_dim.call_args
    assert isinstance(args[0], AboutDialog)
    assert args[1] == parent_widget