import os

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from settings import config
from func.utils import resource_path
from ui.DimmerOverlay import DimmerOverlay

def fade_animation(self):
    # --- EFFETTO FADE-IN (COMPARSA SFUMATA) --- #
    self.setWindowOpacity(0.0)
    
    self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
    self.fade_animation.setDuration(200) # Durata in millisecondi (es. 0.2 secondi)
    self.fade_animation.setStartValue(0.0)
    self.fade_animation.setEndValue(1.0)
    self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    self.fade_animation.start()

def initialize_window(self, w, h):
    self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))
    self.setFixedSize(w, h)

    fade_animation(self)

    self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    if config.get("ALWAYS_ON_TOP", False) == True:
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    else:
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)

def get_overlay(self):
    current_theme = config.get("THEME", "light")
            
    if current_theme == "dark":
        rgba_css = "rgba(0, 0, 0, 130)"
    else:
        rgba_css = "rgba(0, 0, 0, 150)"
        
    overlay = DimmerOverlay(self, rgba_css)
    overlay.show()

    return overlay

def exec_with_parent_dim(dlg, parent):
    overlay = None
    if parent:
        overlay = get_overlay(parent)
    try:
        dlg.exec()
    finally:
        if overlay:
            overlay.deleteLater()