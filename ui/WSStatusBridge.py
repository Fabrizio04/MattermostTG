from PyQt6.QtCore import QObject, pyqtSignal

class WSStatusBridge(QObject):
    # Segnale che emette True (connesso - verde) o False (disconnesso - rosso)
    status_changed = pyqtSignal(bool)

ws_bridge = WSStatusBridge()