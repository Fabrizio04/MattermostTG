from PyQt6.QtCore import Qt
from ui.ToggleSwitch import ToggleSwitch

def test_toggle_switch_init(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    
    assert not switch.isChecked()
    assert switch.width() == 50
    assert switch.height() == 24
    assert switch.get_circle_position() == 3.0
    
    switch.close()

def test_toggle_switch_set_checked(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    
    switch.setChecked(True)
    assert switch.isChecked()
    assert switch.get_circle_position() == 27.0
    
    switch.setChecked(False)
    assert not switch.isChecked()
    assert switch.get_circle_position() == 3.0
    
    switch.close()

def test_toggle_switch_click(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    
    qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)
    
    qtbot.wait(200)
    
    assert switch.isChecked()
    assert switch.get_circle_position() == 27.0
    
    qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)
    qtbot.wait(200)
    
    assert not switch.isChecked()
    assert switch.get_circle_position() == 3.0
    
    switch.close()

def test_toggle_switch_paint_event(qtbot):
    switch = ToggleSwitch()
    qtbot.addWidget(switch)
    
    switch.setChecked(True)
    switch.update()
    
    switch.setChecked(False)
    switch.update()
    
    assert True
    switch.close()