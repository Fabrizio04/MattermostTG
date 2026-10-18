import os
import sys
import signal

# Compatibilità Linux/GNOME: previene il crash di GLib-GIO e i problemi con il display manager
if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_STYLE_OVERRIDE", "Fusion")
    os.environ.setdefault("GSETTINGS_BACKEND", "memory")

from logger import log
from settings import load_settings, config
from func.theme import get_stylesheet
from MattermostApp import MattermostApp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLockFile, QDir, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox

from ui.CustomMessageBox import CustomMessageBox

# Manteniamo il lock file a livello globale per evitare che il Garbage Collector lo elimini
lock_file = None

def main():
    global lock_file
    app = QApplication(sys.argv)
    load_settings()
    app.setStyleSheet(get_stylesheet(config.get("THEME", "light")))
    # app.setStyle("Fusion")

    # Crea un file di lock nella cartella temporanea del sistema
    lock_path = os.path.join(QDir.tempPath(), "MattermostNotifier.lock")
    lock_file = QLockFile(lock_path)

    # Tenta di acquisire il lock senza attendere (tryLock con timeout 0)
    if not lock_file.tryLock(100):
        # Se il lock fallisce, l'app è già in esecuzione
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Icon.Warning)
        # msg.setWindowTitle("Applicazione già in esecuzione")
        # msg.setText("Mattermost Notifier è già attivo nella tray area del sistema in uso.")
        # msg.exec()
        CustomMessageBox.show_warning_on_start("Applicazione già in esecuzione", "Mattermost Notifier è già attivo nella tray area del sistema in uso.")
        sys.exit(0)

    
    app.setQuitOnLastWindowClosed(False)
    notifier = MattermostApp(app)
    log.info("Servizio avviato")

    # Funzione di spegnimento pulito
    def shutdown_gracefully():
        log.info("Chiusura in corso...")
        if hasattr(notifier, 'quit'):
            notifier.quit()
        app.quit()

    # Intercettiamo il Ctrl+C (SIGINT)
    def sigint_handler(signum, frame):
        shutdown_gracefully()

    signal.signal(signal.SIGINT, sigint_handler)

    # Timer periodico che permette a Python di intercettare i segnali 
    # della tastiera anche durante l'esecuzione di app.exec()
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    # Avvio pulito
    sys.exit(app.exec())

if __name__ == "__main__":
    main()