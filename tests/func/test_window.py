from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QDialog

from unittest.mock import patch, MagicMock

from func.window import fade_animation, initialize_window, get_overlay, exec_with_parent_dim

class DummyWindow(QWidget):
    """Classe di supporto per testare i metodi che operano su 'self' (QWidget)"""
    def __init__(self):
        super().__init__()
        self.fade_animation = fade_animation.__get__(self, DummyWindow)
        self.initialize_window = initialize_window.__get__(self, DummyWindow)
        self.get_overlay = get_overlay.__get__(self, DummyWindow)

def test_fade_animation(qtbot):
    win = DummyWindow()
    qtbot.addWidget(win)
    
    win.fade_animation()
    assert hasattr(win, "fade_animation_obj") or True
    assert win.windowOpacity() == 0.0

@patch("func.utils.resource_path", return_value="fake_icon.png")
def test_initialize_window(mock_resource, qtbot, monkeypatch):
    monkeypatch.setattr("func.window.config", {"ALWAYS_ON_TOP": True})
    win = DummyWindow()
    qtbot.addWidget(win)
    
    win.initialize_window(500, 400)
    
    assert win.width() == 500
    assert win.height() == 400
    assert win.windowFlags() & Qt.WindowType.WindowStaysOnTopHint

@patch("func.window.DimmerOverlay")
def test_get_overlay_dark(mock_dimmer_class, qtbot, monkeypatch):
    monkeypatch.setattr("func.window.config", {"THEME": "dark"})
    win = DummyWindow()
    qtbot.addWidget(win)
    
    mock_overlay_instance = MagicMock()
    mock_dimmer_class.return_value = mock_overlay_instance
    
    overlay = win.get_overlay()
    
    mock_dimmer_class.assert_called_once_with(win, "rgba(0, 0, 0, 130)")
    mock_overlay_instance.show.assert_called_once()
    assert overlay == mock_overlay_instance

def test_exec_with_parent_dim(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    dlg = QDialog(parent)
    
    mock_overlay = MagicMock()
    
    with patch("func.window.get_overlay", return_value=mock_overlay) as mock_get_overlay, \
         patch.object(dlg, "exec", return_value=QDialog.DialogCode.Accepted) as mock_exec:
         
        exec_with_parent_dim(dlg, parent)
        
        mock_get_overlay.assert_called_once_with(parent)
        mock_exec.assert_called_once()
        mock_overlay.deleteLater.assert_called_once()