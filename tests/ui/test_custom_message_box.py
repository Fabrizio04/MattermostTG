from unittest.mock import patch
from PyQt6.QtWidgets import QWidget, QPushButton

from ui.CustomMessageBox import CustomMessageBox

def test_custom_message_box_initialization(qtbot):
    for icon_type in ["warning", "critical", "question", "info"]:
        box = CustomMessageBox(title="Test Title", message="Test Message", icon_type=icon_type)
        qtbot.addWidget(box)
        
        assert box.width() == 400
        assert box.selected_button is None

def test_custom_message_box_button_click(qtbot):
    custom_buttons = [("Salva", "save"), ("Annulla", "cancel")]
    box = CustomMessageBox(title="Title", message="Msg", buttons=custom_buttons)
    qtbot.addWidget(box)
    
    buttons = [btn for btn in box.findChildren(QPushButton) if btn.text() in ["Salva", "Annulla"]]
    assert len(buttons) == 2
    
    with patch.object(box, "accept") as mock_accept:
        buttons[0].click()
        assert box.selected_button == "save"
        mock_accept.assert_called_once()

@patch("ui.CustomMessageBox.exec_with_parent_dim")
def test_static_methods_with_parent(mock_exec_dim, qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    CustomMessageBox.show_info(parent, "Info Title", "Info Msg")
    mock_exec_dim.assert_called()

def test_static_method_ask_yes_no(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    
    def side_effect_exec(dlg, p):
        dlg.selected_button = "yes"
        
    with patch("ui.CustomMessageBox.exec_with_parent_dim", side_effect=side_effect_exec):
        result = CustomMessageBox.ask_yes_no(parent, "Title", "Are you sure?")
        assert result == "yes"