from PyQt6.QtCore import QObject, pyqtSignal

class WSStatusBridge(QObject):
    status_changed = pyqtSignal(bool)

ws_bridge = WSStatusBridge()