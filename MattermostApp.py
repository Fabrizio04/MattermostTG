# import os
import threading
import listen_mattermost

from logger import log
from PyQt6.QtGui import QAction
from utils import make_circle_icon, get_tray_icon
from SettingsDialog import SettingsDialog
from PyQt6.QtWidgets import (QSystemTrayIcon, QMenu)

# --- APPLICATION CONTROLLER ---
class MattermostApp:
    def __init__(self, qapp):
        self.qapp = qapp
        self.settings_dialog = None  # Per evitare aperture doppie

        # Tray Icon
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        self.tray_icon.setToolTip("Mattermost Notifier")

        # Menu Contestuale
        self.menu = QMenu()
        
        self.action_active = QAction("Notifiche Attive", self.menu)
        self.action_active.setCheckable(True)
        self.action_active.setChecked(True)
        self.action_active.triggered.connect(self.toggle_service)
        self.menu.addAction(self.action_active)

        self.action_settings = QAction("Impostazioni", self.menu)
        self.action_settings.triggered.connect(self.open_settings)
        self.menu.addAction(self.action_settings)

        self.menu.addSeparator()

        self.action_quit = QAction("Esci", self.menu)
        self.action_quit.triggered.connect(self.quit)
        self.menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

        # Avvio WebSocket
        threading.Thread(target=listen_mattermost.run_websocket_loop, daemon=True).start()

    def toggle_service(self, checked):
        listen_mattermost.service_active = checked
        self.update_icon()

    def update_icon(self):
        self.tray_icon.setIcon(get_tray_icon(listen_mattermost.service_active))

    def open_settings(self):
        # Se la finestra è già aperta, la porta in primo piano senza crearne una nuova
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            self.settings_dialog.activateWindow()
            return

        self.settings_dialog = SettingsDialog()
        self.settings_dialog.exec()
        self.settings_dialog = None

    def quit(self):
        listen_mattermost.running = False
        self.tray_icon.hide()
        self.qapp.quit()
        log.info("Servizio terminato")
        #os._exit(0)