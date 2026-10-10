# import os
import threading
import listen_mattermost

from logger import log
from PyQt6.QtGui import QAction
from ui.AboutDialog import AboutDialog
from ui.SettingsDialog import SettingsDialog
from func.utils import make_circle_icon, get_tray_icon
from PyQt6.QtWidgets import (QSystemTrayIcon, QMenu)

# --- APPLICATION CONTROLLER ---
class MattermostApp:
    def __init__(self, qapp):
        self.qapp = qapp
        self.settings_dialog = None  # Per evitare aperture doppie
        self.about_dialog = None  # Per evitare aperture doppie

        # Tray Icon
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        self.tray_icon.setToolTip("Mattermost Notifier")
        self.tray_icon.activated.connect(self.on_tray_activated)

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

        self.action_about = QAction("Informazioni...", self.menu)
        self.action_about.triggered.connect(self.open_about)
        self.menu.addAction(self.action_about)

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

    def on_tray_activated(self, reason):
        # Se l'utente fa doppio clic, inattiva/attiva il servizio al volo
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            new_state = not listen_mattermost.service_active
            # Aggiorna anche la spunta nel menu contestuale per coerenza
            self.action_active.setChecked(new_state)
            self.toggle_service(new_state)

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

    def open_about(self):
        if self.about_dialog is not None and self.about_dialog.isVisible():
            self.about_dialog.activateWindow()
            return

        self.about_dialog = AboutDialog()
        self.about_dialog.exec()
        self.about_dialog = None

    def quit(self):
        listen_mattermost.running = False
        self.tray_icon.hide()
        self.qapp.quit()
        log.info("Servizio terminato")
        #os._exit(0)