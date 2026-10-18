from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

class DimmerOverlay(QWidget):
    """Un pannello semitrasparente che copre la finestra genitore per oscurarla durante i popup"""
    def __init__(self, parent, rgba_css):
        super().__init__(parent)
        # ATTRIBUTO FONDAMENTALE: Forza PyQt a disegnare il background-color con trasparenza (RGBA)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self.setGeometry(parent.rect())
        self.setStyleSheet(f"background-color: {rgba_css}; border-radius: 12px;")
        parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == event.Type.Resize:
            self.setGeometry(self.parent().rect())
        return super().eventFilter(obj, event)