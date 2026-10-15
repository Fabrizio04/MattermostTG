# import os
import threading
import mattermost_listener

from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QLabel,
    QWidget, QHBoxLayout, QWidgetAction
)

from logger import log
from PyQt6.QtGui import QAction
from ui.WSStatusBridge import ws_bridge
from ui.SettingsDialog import SettingsDialog
from func.utils import make_circle_icon, get_tray_icon

# --- APPLICATION CONTROLLER ---
class MattermostApp:
    def __init__(self, qapp):
        self.qapp = qapp
        self.settings_dialog = None  # Per evitare aperture doppie

        # Tray Icon
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        self.tray_icon.setToolTip("Mattermost Notifier")
        self.tray_icon.activated.connect(self.on_tray_activated)

        # Menu Contestuale
        self.menu = QMenu()

        # self.tray_ws_action = QAction("Stato WS: Connessione...", self.menu)
        # self.tray_ws_action.setEnabled(False)
        # self.action_active.setCheckable(True)
        # self.menu.addAction(self.tray_ws_action)

        # 1. Creiamo un widget contenitore per la riga del menu
        tray_ws_widget = QWidget()
        tray_ws_layout = QHBoxLayout(tray_ws_widget)
        # Margini simili alle voci di menu standard di Windows
        tray_ws_layout.setContentsMargins(22, 4, 10, 4) 
        tray_ws_layout.setSpacing(8)

        # 2. Il nostro pallino (uguale a quello delle impostazioni!)
        self.tray_ws_dot = QLabel()
        self.tray_ws_dot.setFixedSize(10, 10)
        self.tray_ws_dot.setStyleSheet("background-color: #e63946; border-radius: 5px;")

        # 3. L'etichetta del testo
        self.tray_ws_label = QLabel("Mattermost: Disconnesso")

        tray_ws_layout.addWidget(self.tray_ws_dot)
        tray_ws_layout.addWidget(self.tray_ws_label)
        tray_ws_layout.addStretch()

        # 4. Creiamo la QWidgetAction e associamo il widget
        self.tray_ws_action = QWidgetAction(self.menu)
        self.tray_ws_action.setDefaultWidget(tray_ws_widget)
        # Rendiamo l'azione non cliccabile
        self.tray_ws_action.setEnabled(False)

        # Inseriamo in cima al menu
        self.menu.addAction(self.tray_ws_action)
        self.menu.addSeparator()
        
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
        threading.Thread(target=mattermost_listener.run_websocket_loop, daemon=True).start()

        ws_bridge.status_changed.connect(self.update_tray_ws_status)
        self.update_tray_ws_status(mattermost_listener.is_websocket_connected())

    def update_tray_ws_status(self, is_connected: bool):
        if is_connected:
            self.tray_ws_dot.setStyleSheet("background-color: #2a9d8f; border-radius: 5px;")
            self.tray_ws_label.setText("Mattermost: Connesso")
        else:
            self.tray_ws_dot.setStyleSheet("background-color: #e63946; border-radius: 5px;")
            self.tray_ws_label.setText("Mattermost: Disconnesso")

    def toggle_service(self, checked):
        mattermost_listener.service_active = checked
        self.update_icon()
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            if self.settings_dialog and hasattr(self.settings_dialog, "update_menu_toggle_notification"):
                self.settings_dialog.update_menu_toggle_notification(checked)
                self.settings_dialog.activateWindow()
                self.settings_dialog.raise_()

    def on_tray_activated(self, reason):
        # Se l'utente fa doppio clic, inattiva/attiva il servizio al volo
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            new_state = not mattermost_listener.service_active
            # Aggiorna anche la spunta nel menu contestuale per coerenza
            self.action_active.setChecked(new_state)
            self.toggle_service(new_state)

    def update_icon(self):
        self.tray_icon.setIcon(get_tray_icon(mattermost_listener.service_active))

    def open_settings(self):
        # Se la finestra è già aperta, la porta in primo piano senza crearne una nuova
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            self.settings_dialog.activateWindow()
            self.settings_dialog.raise_()
            return

        self.settings_dialog = SettingsDialog(controller=self)
        # self.settings_dialog.exec()
        # self.settings_dialog = None
        self.settings_dialog.finished.connect(lambda: setattr(self, 'settings_dialog', None))
        self.settings_dialog.show()

    def quit(self):
        mattermost_listener.running = False
        self.tray_icon.hide()
        self.qapp.quit()
        log.info("Servizio terminato")
        #os._exit(0)