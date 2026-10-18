import threading
import mattermost_listener

from logger import log
from PyQt6.QtGui import QAction
from ui.WSStatusBridge import ws_bridge
from ui.SettingsDialog import SettingsDialog
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from func.utils import make_circle_icon, get_tray_icon
from func.message_queue import start_retry_worker, stop_retry_worker

from settings import config
from func.theme import get_stylesheet

# --- APPLICATION CONTROLLER ---
class MattermostApp:
    def __init__(self, qapp):
        self.qapp = qapp
        self.settings_dialog = None

        # Tray Icon
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        self.tray_icon.setToolTip("Mattermost Notifier")
        self.tray_icon.activated.connect(self.on_tray_activated)

        # Menu Contestuale
        self.menu = QMenu()

        # Creiamo un'azione di sola lettura standard (funziona sia su Windows che su Linux)
        self.tray_ws_action = QAction("Mattermost: Disconnesso", self.menu)
        self.tray_ws_action.setEnabled(False)
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
        start_retry_worker()

        ws_bridge.status_changed.connect(self.update_tray_ws_status)
        self.update_tray_ws_status(mattermost_listener.is_websocket_connected())

    def update_tray_ws_status(self, is_connected: bool):
        if is_connected:
            self.tray_ws_action.setText("🟢 Mattermost: Connesso")
        else:
            self.tray_ws_action.setText("🔴 Mattermost: Disconnesso")

    def toggle_service(self, checked):
        mattermost_listener.service_active = checked
        self.action_active.setChecked(checked)
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
        self.settings_dialog.finished.connect(lambda: setattr(self, 'settings_dialog', None))
        self.settings_dialog.show()

    def on_save_settings(self):
        log.debug("on_save_settings")
        self.qapp.setStyleSheet(get_stylesheet(config.get("THEME", "light")))

    def quit(self):
        mattermost_listener.running = False
        stop_retry_worker()
        self.tray_icon.hide()
        self.qapp.quit()
        log.info("Servizio terminato")
        #os._exit(0)