from settings import config
from ui.ToggleSwitch import ToggleSwitch
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

def create_toggle_row(label_text, default_val, fallback = True):
    container = QWidget()
    container.setFixedHeight(30)

    h_layout = QHBoxLayout(container)
    h_layout.setContentsMargins(0, 0, 0, 0)  # Rimuove margini superflui

    lbl = QLabel(label_text)
    toggle = ToggleSwitch()
    toggle.setChecked(config.get(default_val, fallback))

    h_layout.addWidget(lbl)
    h_layout.addStretch()
    h_layout.addWidget(toggle)

    return container, lbl, toggle