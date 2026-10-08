import os
import sys

from logger import log
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor


# --- UTILS ICONA ---
def make_circle_icon(active=True):
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    color = QColor(0, 180, 216) if active else QColor(120, 120, 120)
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(8, 8, 48, 48)
    painter.end()
    return QIcon(pixmap)

def resource_path(relative_path):
    """ Ottiene il percorso assoluto delle risorse, funziona sia in dev che con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_tray_icon(active=True):
    # Seleziona l'estensione più adatta all'OS
    ext = "ico" if sys.platform.startswith("win") else "png"
    filename = f"icon_active.{ext}" if active else f"icon_inactive.{ext}"
    relative_path = os.path.join("img", filename)
    path = resource_path(relative_path)
    
    # Verifica di sicurezza: se il file esiste lo carica, altrimenti restituisce un'icona vuota
    if os.path.exists(path):
        return QIcon(path)
    else:
        log.warning(f"File icona non trovato: {path}")
        return QIcon()