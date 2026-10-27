from unittest.mock import patch
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel

from ui.CustomTitleBar import CustomTitleBar

def test_custom_title_bar_init(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    with patch("ui.CustomTitleBar.resource_path", return_value="fake_icon.png"):
        with patch.object(QLabel, "setPixmap"):
            title_bar = CustomTitleBar(parent=parent, title="Il mio titolo")
            qtbot.addWidget(title_bar)
            
            assert title_bar.title_label.text() == "Il mio titolo"
            
            close_btn = title_bar.findChild(QPushButton, "TitleBarCloseBtn")
            assert close_btn is not None

def test_custom_title_bar_close_action(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    with patch("ui.CustomTitleBar.resource_path", return_value="fake_icon.png"), \
         patch.object(QLabel, "setPixmap"), \
         patch.object(parent, "close") as mock_close:
         
        title_bar = CustomTitleBar(parent=parent, title="Test")
        qtbot.addWidget(title_bar)
        
        close_btn = title_bar.findChild(QPushButton, "TitleBarCloseBtn")
        close_btn.click()
        
        mock_close.assert_called_once()

def test_custom_title_bar_dragging(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    with patch("ui.CustomTitleBar.resource_path", return_value="fake_icon.png"), \
         patch.object(QLabel, "setPixmap"), \
         patch.object(parent, "move") as mock_move:
         
        title_bar = CustomTitleBar(parent=parent, title="Test")
        qtbot.addWidget(title_bar)
        
        press_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(10.0, 10.0),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        title_bar.mousePressEvent(press_event)
        
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(50.0, 50.0),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        title_bar.mouseMoveEvent(move_event)
        
        mock_move.assert_called()