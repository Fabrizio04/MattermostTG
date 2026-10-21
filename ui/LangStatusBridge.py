from PyQt6.QtCore import QObject, pyqtSignal

class LangStatusBridge(QObject):
    status_changed = pyqtSignal(str)

i18n_bridge = LangStatusBridge()