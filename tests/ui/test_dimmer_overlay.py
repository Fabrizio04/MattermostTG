from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QResizeEvent

from ui.DimmerOverlay import DimmerOverlay

def test_dimmer_overlay_init(qtbot):
    parent = QWidget()
    parent.resize(500, 400)
    qtbot.addWidget(parent)
    
    overlay = DimmerOverlay(parent=parent, rgba_css="rgba(0, 0, 0, 100)")
    qtbot.addWidget(overlay)
    
    assert overlay.geometry() == parent.rect()

def test_dimmer_overlay_resize_event_filter(qtbot):
    parent = QWidget()
    parent.resize(300, 300)
    qtbot.addWidget(parent)
    
    overlay = DimmerOverlay(parent=parent, rgba_css="rgba(0, 0, 0, 150)")
    qtbot.addWidget(overlay)
    
    parent.resize(600, 500)
    
    resize_event = QResizeEvent(parent.size(), QWidget.size(parent))
    overlay.eventFilter(parent, resize_event)
    
    assert overlay.geometry() == parent.rect()
    assert overlay.width() == 600
    assert overlay.height() == 500