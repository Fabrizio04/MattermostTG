import sys

from settings import load_settings
from MattermostApp import MattermostApp
from PyQt6.QtWidgets import QApplication

from logger import log

if __name__ == "__main__":
    load_settings()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    notifier = MattermostApp(app)
    log.info("Servizio avviato")
    sys.exit(app.exec())