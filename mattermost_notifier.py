import os
import sys
import signal
import mattermost_listener

if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_STYLE_OVERRIDE", "Fusion")
    os.environ.setdefault("GSETTINGS_BACKEND", "memory")

from logger import log
from settings import load_settings, config

from func.i18n import load_language, get
from func.theme import get_stylesheet
from func.parse_args import parse_args

from MattermostApp import MattermostApp
from HeadlessHTTPServer import HeadlessHTTPServer

from PyQt6.QtCore import QLockFile, QDir, QTimer

lock_file = None

def main():
    global lock_file

    args = parse_args()
    load_settings(args)
    load_language()

    if args.headless:
        from PyQt6.QtCore import QCoreApplication
        app = QCoreApplication(sys.argv)
        log.info(f"[HEADLESS] {get('main.headless')}")
    else:
        from PyQt6.QtWidgets import QApplication
        from ui.CustomMessageBox import CustomMessageBox
        app = QApplication(sys.argv)

    if not args.headless:
        app.setStyleSheet(get_stylesheet(config.get("THEME", "light")))
        # app.setStyle("Fusion")

    lock_path = os.path.join(QDir.tempPath(), "MattermostNotifier.lock")
    lock_file = QLockFile(lock_path)

    if not lock_file.tryLock(100):
        if args.headless:
            log.warning(get("main.lock_headless_msg"))
        else:
            CustomMessageBox.show_warning_on_start(get("main.lock_title"), get("main.lock_message"))
        sys.exit(0)

    if args.headless:
        import threading
        from func.message_queue import start_retry_worker
        threading.Thread(target=mattermost_listener.run_websocket_loop, daemon=True).start()
        start_retry_worker()
        threading.Thread(target=HeadlessHTTPServer.run_http_server, daemon=True).start()
        log.info(get("log.service.started"))
    else:
        app.setQuitOnLastWindowClosed(False)
        notifier = MattermostApp(app)
        log.info(get("log.service.started"))

        if args.open_settings:
            QTimer.singleShot(100, notifier.open_settings)
    

    def shutdown_gracefully():
        log.info(get("log.service.closing"))

        if not args.headless and 'notifier' in locals() and hasattr(notifier, 'quit'):
            notifier.quit()
        else:
            mattermost_listener.running = False
            from func.message_queue import stop_retry_worker
            stop_retry_worker()
            HeadlessHTTPServer.stop_http_server()
            log.info(get("log.service.ended"))

        app.quit()

    def sigint_handler(signum, frame):
        shutdown_gracefully()

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()