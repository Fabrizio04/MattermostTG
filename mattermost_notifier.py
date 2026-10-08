import os
import sys

# Compatibilità Linux/GNOME: previene il crash di GLib-GIO e i problemi con il display manager
if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_STYLE_OVERRIDE", "Fusion")
    os.environ.setdefault("GSETTINGS_BACKEND", "memory")

from settings import load_settings
from MattermostApp import MattermostApp
from PyQt6.QtWidgets import QApplication

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QLockFile, QDir

from logger import log

# Manteniamo il lock file a livello globale per evitare che il Garbage Collector lo elimini
lock_file = None

def main():
    global lock_file
    app = QApplication(sys.argv)

    # Crea un file di lock nella cartella temporanea del sistema
    lock_path = os.path.join(QDir.tempPath(), "MattermostNotifier.lock")
    lock_file = QLockFile(lock_path)

    # Tenta di acquisire il lock senza attendere (tryLock con timeout 0)
    if not lock_file.tryLock(100):
        # Se il lock fallisce, l'app è già in esecuzione
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Applicazione già in esecuzione")
        msg.setText("Mattermost Notifier è già attivo nella tray area del sistema in uso.")
        msg.exec()
        sys.exit(0)

    load_settings()
    app.setQuitOnLastWindowClosed(False)
    notifier = MattermostApp(app)
    log.info("Servizio avviato")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()