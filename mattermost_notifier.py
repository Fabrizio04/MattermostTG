import os
import sys
import signal

if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_STYLE_OVERRIDE", "Fusion")
    os.environ.setdefault("GSETTINGS_BACKEND", "memory")

from logger import log
from settings import load_settings, config

from func.i18n import load_language, get
from func.theme import get_stylesheet

from MattermostApp import MattermostApp

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLockFile, QDir, QTimer

from ui.CustomMessageBox import CustomMessageBox

lock_file = None

def main():
    global lock_file
    app = QApplication(sys.argv)
    load_settings()
    app.setStyleSheet(get_stylesheet(config.get("THEME", "light")))
    load_language()
    # app.setStyle("Fusion")

    lock_path = os.path.join(QDir.tempPath(), "MattermostNotifier.lock")
    lock_file = QLockFile(lock_path)

    if not lock_file.tryLock(100):
        CustomMessageBox.show_warning_on_start(get("main.lock_title"), get("main.lock_message"))
        sys.exit(0)

    
    app.setQuitOnLastWindowClosed(False)
    notifier = MattermostApp(app)
    log.info(get("log.service.started"))

    if "--open-settings" in sys.argv:
        QTimer.singleShot(100, notifier.open_settings)

    def shutdown_gracefully():
        log.info(get("log.service.closing"))
        if hasattr(notifier, 'quit'):
            notifier.quit()
        app.quit()

    # Ctrl+C (SIGINT)
    def sigint_handler(signum, frame):
        shutdown_gracefully()

    signal.signal(signal.SIGINT, sigint_handler)

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    # Avvio pulito
    sys.exit(app.exec())

if __name__ == "__main__":
    main()