from ui.ToggleSwitch import ToggleSwitch
from PyQt6.QtWidgets import QWidget, QLabel
from func.create_toggle_row import create_toggle_row

def test_create_toggle_row_structure_and_fallback(qtbot, monkeypatch):
    monkeypatch.setattr("func.create_toggle_row.config", {})
    
    container, lbl, toggle = create_toggle_row("Abilita notifiche", "NOTIF_KEY", fallback=True)
    
    assert isinstance(container, QWidget)
    assert isinstance(lbl, QLabel)
    assert isinstance(toggle, ToggleSwitch)
    assert lbl.text() == "Abilita notifiche"
    assert toggle.isChecked() is True

def test_create_toggle_row_with_config_value(qtbot, monkeypatch):
    monkeypatch.setattr("func.create_toggle_row.config", {"DARK_MODE_ENABLED": False})
    container, lbl, toggle = create_toggle_row("Tema scuro", "DARK_MODE_ENABLED", fallback=True)
    
    assert lbl.text() == "Tema scuro"
    assert toggle.isChecked() is False