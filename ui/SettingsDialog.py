import os
import shutil
import keyring
import mattermost_listener

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QGroupBox, QLineEdit,
    QVBoxLayout, QFileDialog, QMenuBar,
    QGridLayout, QWidget, QHBoxLayout
)

from settings import (
    APP_NAME, CONFIG_FILE_PATH, config,
    save_settings, reset_settings
)

from logger import log

from func.utils import resource_path
from func.i18n import get, load_language
from func.aes import get_or_create_aes_key
from func.check_on_close import check_on_close
from func.create_toggle_row import create_toggle_row
from func.get_system_locale import get_system_locale
from func.window import initialize_window, get_overlay

from ui.AboutDialog import AboutDialog
from ui.WSStatusBridge import ws_bridge
from ui.LangStatusBridge import i18n_bridge
from ui.CustomTitleBar import CustomTitleBar
from ui.LanguageDialog import LanguageDialog
from ui.LogViewerDialog import LogViewerDialog
from ui.CustomMessageBox import CustomMessageBox
from ui.ExcludedListDialog import ExcludedListDialog
from ui.TimeoutSettingsDialog import TimeoutSettingsDialog


# --- FINESTRA IMPOSTAZIONI --- #
class SettingsDialog(QDialog):

    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.log_dialog = None

        initialize_window(self, 450, 550)

        self.menu_bar = QMenuBar(self)

        #region --- MENU FILE --- #
        menu_file = self.menu_bar.addMenu("File")
        
        self.act_import = QAction(get("settings.menubar.file.import"), self)
        self.act_import.triggered.connect(self.import_settings_json)
        menu_file.addAction(self.act_import)
        
        self.act_export = QAction(get("settings.menubar.file.export"), self)
        self.act_export.triggered.connect(self.export_settings_json)
        menu_file.addAction(self.act_export)
        
        menu_file.addSeparator()
        
        self.act_exit = QAction(get("settings.menubar.file.exit"), self)
        self.act_exit.triggered.connect(self.close)
        menu_file.addAction(self.act_exit)
        #endregion

        #region --- MENU MODIFICA --- #
        self.menu_edit = self.menu_bar.addMenu(get("settings.menubar.edit.title"))
        
        self.act_notif = QAction(get("settings.menubar.edit.notifications_active"), self)
        self.act_notif.setCheckable(True)
        self.act_notif.triggered.connect(self.toggle_notifications_from_menu)
        self.act_notif.setChecked(mattermost_listener.service_active)
        self.menu_edit.addAction(self.act_notif)
        
        self.act_senders = QAction(get("settings.menubar.edit.senders_discard"), self)
        self.act_senders.triggered.connect(lambda: self.open_excluded_dialog("senders"))
        self.menu_edit.addAction(self.act_senders)
        
        self.act_channels = QAction(get("settings.menubar.edit.channels_discard"), self)
        self.act_channels.triggered.connect(lambda: self.open_excluded_dialog("channels"))
        self.menu_edit.addAction(self.act_channels)
        
        self.menu_edit.addSeparator()
        
        self.act_reset = QAction(get("settings.menubar.edit.default_settings"), self)
        self.act_reset.triggered.connect(self.reset_settings)
        self.menu_edit.addAction(self.act_reset)
        #endregion

        #region --- MENU VISUALIZZA --- #
        self.menu_view = self.menu_bar.addMenu(get("settings.menubar.view.title"))

        self.on_top_window = QAction(get("settings.menubar.view.always_on_top"), self)
        self.on_top_window.setCheckable(True)
        self.on_top_window.triggered.connect(self.update_on_top_window)
        self.on_top_window.setChecked(config.get("ALWAYS_ON_TOP", False))
        self.menu_view.addAction(self.on_top_window)

        self.theme = QAction(get("settings.menubar.view.theme"), self)
        self.theme.triggered.connect(self.update_theme)
        self.menu_view.addAction(self.theme)

        self.language = QAction(get("settings.menubar.view.language"), self)
        self.language.triggered.connect(self.update_language)
        self.menu_view.addAction(self.language)
        #endregion

        #region --- MENU AVANZATE ---
        self.menu_advanced = self.menu_bar.addMenu(get("settings.menubar.advanced.title"))
        
        self.act_timeout = QAction(get("settings.menubar.advanced.timeout"), self)
        self.act_timeout.triggered.connect(self.open_timeout_settings)
        self.menu_advanced.addAction(self.act_timeout)
        
        self.act_logs = QAction(get("settings.menubar.advanced.log"), self)
        self.act_logs.triggered.connect(self.open_log)
        self.menu_advanced.addAction(self.act_logs)
        #endregion

        #region --- MENU AES-256 ---
        self.menu_aes = self.menu_bar.addMenu(get("settings.menubar.aes.title"))
        
        self.act_regen_key = QAction(get("settings.menubar.aes.regeneration"), self)
        self.act_regen_key.triggered.connect(self.regenerate_aes_key)
        self.menu_aes.addAction(self.act_regen_key)
        
        self.act_download_key = QAction(get("settings.menubar.aes.download1"), self)
        self.act_download_key.triggered.connect(self.download_raw_key)
        self.menu_aes.addAction(self.act_download_key)
        
        self.act_download_dec = QAction(get("settings.menubar.aes.download2"), self)
        self.act_download_dec.triggered.connect(lambda: self.download_decrypter_html(False))
        self.menu_aes.addAction(self.act_download_dec)
        
        self.act_download_dec_key = QAction(get("settings.menubar.aes.download3"), self)
        self.act_download_dec_key.triggered.connect(lambda: self.download_decrypter_html(True))
        self.menu_aes.addAction(self.act_download_dec_key)
        #endregion

        #region --- MENU AIUTO ---
        self.menu_help = self.menu_bar.addMenu(get("settings.menubar.help.title"))
        
        self.act_updates = QAction(get("settings.menubar.help.update"), self)
        self.menu_help.addAction(self.act_updates)
        
        self.act_about = QAction(get("settings.menubar.help.about"), self)
        self.act_about.triggered.connect(self.open_about)
        self.menu_help.addAction(self.act_about)
        #endregion

        # Stati connessione
        status_container = QWidget()
        status_container.setFixedHeight(24)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 10, 0)
        status_layout.setSpacing(6)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Indicatore 1: Stato Websocket
        self.ws_indicator = QLabel()
        self.ws_indicator.setFixedSize(10, 10)
        self.ws_indicator.setStyleSheet("background-color: #e63946; border-radius: 5px;")
        self.ws_indicator.setToolTip(get("settings.ui.marker_ws.disconnected"))

        # Indicatore 2: Stato Servizio
        self.service_indicator = QLabel()
        self.service_indicator.setFixedSize(10, 10)
        self.service_indicator.setStyleSheet("background-color: #adb5bd; border-radius: 5px;")
        self.service_indicator.setToolTip(get("settings.ui.marker_srv.inactive"))

        status_layout.addWidget(self.ws_indicator)
        status_layout.addWidget(self.service_indicator)

        self.menu_bar.setCornerWidget(status_container, Qt.Corner.TopRightCorner)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title=get("settings.title"))
        container_layout.addWidget(self.title_bar)

        container_layout.addWidget(self.menu_bar)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)

        # WS URL
        self.txt_ws_url = QLineEdit(config.get("MATTERMOST_WS_URL", ""))
        self.txt_ws_url.setPlaceholderText(get("settings.ui.ws_url_placeholder"))

        # MM Token
        self.txt_mm_token = QLineEdit(config.get("MATTERMOST_TOKEN", ""))
        self.txt_mm_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_mm_token.setPlaceholderText("MATTERMOST_TOKEN")

        # TG Token
        self.txt_tg_token = QLineEdit(config.get("TELEGRAM_BOT_TOKEN", ""))
        self.txt_tg_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_tg_token.setPlaceholderText("bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

        # TG Chat ID
        self.txt_tg_chat_id = QLineEdit(config.get("TELEGRAM_CHAT_ID", ""))
        self.txt_tg_chat_id.setPlaceholderText("123456789")

        grid_layout = QGridLayout()
        
        labels_texts = [
            ("Mattermost WS URL:", self.txt_ws_url),
            ("Mattermost Token:", self.txt_mm_token),
            ("Telegram Bot Token:", self.txt_tg_token),
            ("Telegram Chat ID:", self.txt_tg_chat_id)
        ]

        for row, (label_text, line_edit) in enumerate(labels_texts):
            lbl = QLabel(label_text)
            lbl.setFixedWidth(130) 
            grid_layout.addWidget(lbl, row, 0)
            
            line_edit.setMinimumWidth(260)
            grid_layout.addWidget(line_edit, row, 1)

        layout.addLayout(grid_layout)

        # Crittografia AES-256
        self.row_aes, self.lbl_aes, self.toggle_aes = create_toggle_row(get("settings.ui.toggle_aes"), "AES_ENCRYPTION_ENABLED", False)
        layout.addWidget(self.row_aes)

        # Checkbox Echo Suppression
        self.row_echo, self.lbl_echo, self.chk_echo = create_toggle_row(get("settings.ui.chk_echo"), "ECHO_SUPPRESSION_ENABLED")
        layout.addWidget(self.row_echo)

        # Checkbox modalità anonima
        self.row_anon, self.lbl_anon, self.toggle_anon = create_toggle_row(get("settings.ui.toggle_anon"), "ANONYMOUS_MODE")
        self.toggle_anon.stateChanged.connect(lambda state: self.toggle_anonymous_mode(state))
        layout.addWidget(self.row_anon)

        # GroupBox per i campi granulari
        self.group_granular = QGroupBox(get("settings.ui.group_granular"))
        vbox_granular = QVBoxLayout()

        # Canale, Mittente e Messaggio
        self.row_channel, self.lbl_channel, self.toggle_channel = create_toggle_row(get("settings.ui.toggle_channel"), "INCLUDE_CHANNEL")
        self.row_sender, self.lbl_sender, self.toggle_sender = create_toggle_row(get("settings.ui.toggle_sender"), "INCLUDE_SENDER") 
        self.row_message, self.lbl_message, self.toggle_message = create_toggle_row(get("settings.ui.toggle_message"), "INCLUDE_MESSAGE")
        
        vbox_granular.addWidget(self.row_channel)
        vbox_granular.addWidget(self.row_sender)
        vbox_granular.addWidget(self.row_message)

        self.group_granular.setLayout(vbox_granular)
        layout.addWidget(self.group_granular)

        self.toggle_anonymous_mode(self.toggle_anon.isChecked())

        # Bottone Salva
        self.btn_save = QPushButton(get("settings.ui.btn_save"))
        self.btn_save.setStyleSheet("background-color: #00b4d8; color: #f3f3f3; padding: 8px; font-weight: bold;")
        self.btn_save.clicked.connect(lambda: self.save())
        layout.addWidget(self.btn_save)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        ws_bridge.status_changed.connect(self.update_ws_indicator_ui)
        self.update_ws_indicator_ui(mattermost_listener.is_websocket_connected())
        self.update_service_indicator_ui(mattermost_listener.service_active)

        i18n_bridge.status_changed.connect(self.update_ui)

    def update_ui(self):
        self.title_bar.title_label.setText(get("settings.title"))

        self.act_import.setText(get("settings.menubar.file.import"))
        self.act_export.setText(get("settings.menubar.file.export"))
        self.act_exit.setText(get("settings.menubar.file.exit"))

        self.menu_edit.setTitle(get("settings.menubar.edit.title"))
        self.act_notif.setText(get("settings.menubar.edit.notifications_active"))
        self.act_senders.setText(get("settings.menubar.edit.senders_discard"))
        self.act_channels.setText(get("settings.menubar.edit.channels_discard"))
        self.act_reset.setText(get("settings.menubar.edit.default_settings"))

        self.menu_view.setTitle(get("settings.menubar.view.title"))
        self.on_top_window.setText(get("settings.menubar.view.always_on_top"))
        self.theme.setText(get("settings.menubar.view.theme"))
        self.language.setText(get("settings.menubar.view.language"))

        self.menu_advanced.setTitle(get("settings.menubar.advanced.title"))
        self.act_timeout.setText(get("settings.menubar.advanced.timeout"))
        self.act_logs.setText(get("settings.menubar.advanced.log"))

        self.menu_aes.setTitle(get("settings.menubar.aes.title"))
        self.act_regen_key.setText(get("settings.menubar.aes.regeneration"))
        self.act_download_key.setText(get("settings.menubar.aes.download1"))
        self.act_download_dec.setText(get("settings.menubar.aes.download2"))
        self.act_download_dec_key.setText(get("settings.menubar.aes.download3"))

        self.menu_help.setTitle(get("settings.menubar.help.title"))
        self.act_updates.setText(get("settings.menubar.help.update"))
        self.act_about.setText(get("settings.menubar.help.about"))

        self.txt_ws_url.setPlaceholderText(get("settings.ui.ws_url_placeholder"))
        self.lbl_aes.setText(get("settings.ui.toggle_aes"))
        self.lbl_echo.setText(get("settings.ui.chk_echo"))
        self.lbl_anon.setText(get("settings.ui.toggle_anon"))
        self.group_granular.setTitle(get("settings.ui.group_granular"))
        self.lbl_channel.setText(get("settings.ui.toggle_channel"))
        self.lbl_sender.setText(get("settings.ui.toggle_sender"))
        self.lbl_message.setText(get("settings.ui.toggle_message"))
        self.btn_save.setText(get("settings.ui.btn_save"))

        self.update_ws_indicator_ui(mattermost_listener.is_websocket_connected())
        self.update_service_indicator_ui(mattermost_listener.service_active)

    def export_settings_json(self):
        overlay = get_overlay(self)

        file_path, _ = QFileDialog.getSaveFileName(self, get("settings.export.caption"), "mattermosttg_settings.json", "JSON Files (*.json)")
        if file_path:
            try:
                if os.path.exists(CONFIG_FILE_PATH):
                    shutil.copy(CONFIG_FILE_PATH, file_path)
                    CustomMessageBox.show_info(self, get("settings.export.info.title"), get("settings.export.info.message"))
                else:
                    CustomMessageBox.show_warning(self, get("settings.export.warning.title"), get("settings.export.warning.message"))
            except Exception as e:
                CustomMessageBox.show_critical(self, get("settings.export.critical.title"), f"{get("settings.export.critical.message")} {e}")

        if overlay:
            overlay.deleteLater()

    def import_settings_json(self):
        overlay = get_overlay(self)
        
        file_path, _ = QFileDialog.getOpenFileName(self, get("settings.import.caption"), "", "JSON Files (*.json)")
        if file_path:
            try:
                shutil.copy(file_path, CONFIG_FILE_PATH)
                from settings import load_settings # O ricarica config
                load_settings()
                #ricaricare la UI...
                CustomMessageBox.show_info(self, get("settings.import.info.title"), get("settings.import.info.message"))
            except Exception as e:
                CustomMessageBox.show_critical(self, get("settings.import.critical.title"), f"{get("settings.import.critical.message")} {e}")

        if overlay:
            overlay.deleteLater()

    def regenerate_aes_key(self):
        confirm = CustomMessageBox.ask_yes_no(self, get("settings.aes.regeneration.ask.title"), get("settings.aes.regeneration.ask.message"))
        if confirm == "yes":
            try:
                try:
                    keyring.delete_password(APP_NAME, "AES_ENCRYPTION_KEY")
                except Exception:
                    pass
                get_or_create_aes_key()
                CustomMessageBox.show_info(self, get("settings.aes.regeneration.info.title"), get("settings.aes.regeneration.info.message"))
            except Exception as e:
                CustomMessageBox.show_critical(self, get("settings.aes.regeneration.critical.title"), f"{get("settings.aes.regeneration.critical.message")} {e}")

    def download_raw_key(self):
        user_key = get_or_create_aes_key()
        overlay = get_overlay(self)
        file_path, _ = QFileDialog.getSaveFileName(self, get("settings.aes.key.caption"), f"{get("settings.aes.key.filename")}.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(user_key)
            CustomMessageBox.show_info(self, get("settings.aes.key.info.title"), get("settings.aes.key.info.message"))

        if overlay:
            overlay.deleteLater()

    def toggle_anonymous_mode(self, state):
        is_checked = (state == 2 or state is True)
        self.group_granular.setEnabled(not is_checked)

    def download_decrypter_html(self, includeKey):

        overlay = None
        template_path = resource_path(os.path.join("aes", "decrypter.html"))
        
        if not os.path.exists(template_path):
            CustomMessageBox.show_warning(self, get("settings.aes.decrypter.warning.title"), get("settings.aes.decrypter.warning.message"))
            return

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            chiave_esempio = "===MY_PRIVATE_KEY==="
            if chiave_esempio in html_content:
                html_content = html_content.replace(chiave_esempio, get_or_create_aes_key() if includeKey == True else "")
            else:
                pass

            overlay = get_overlay(self)
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                get("settings.aes.decrypter.caption"),
                f"{get("settings.aes.decrypter.filename")}.html",
                "File HTML (*.html)"
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                CustomMessageBox.show_info(self, get("settings.aes.decrypter.info.title"), f"{get("settings.aes.decrypter.info.message")}\n{file_path}")

        except Exception as e:
            CustomMessageBox.show_critical(self, get("settings.aes.decrypter.critical.title"), f"{get("settings.aes.decrypter.critical.message")} {e}")

        if overlay:
            overlay.deleteLater()

    def toggle_notifications_from_menu(self, checked):
        if self.controller and hasattr(self.controller, "toggle_service"):
            self.controller.toggle_service(checked)
            self.update_service_indicator_ui(checked)

    def update_menu_toggle_notification(self, checked):
        self.act_notif.setChecked(checked)
        self.update_service_indicator_ui(checked)

    def update_on_top_window(self, checked):
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            
        self.setWindowFlags(flags)
        self.show()
        self.save(False)

    def open_excluded_dialog(self, list_type):
        ExcludedListDialog.open_ExcludedListDialog(list_type, self)

    def open_timeout_settings(self):
        TimeoutSettingsDialog.open_TimeoutSettingsDialog(self)

    def open_log(self):
        if self.log_dialog is not None and self.log_dialog.isVisible():
            self.log_dialog.activateWindow()
            self.log_dialog.raise_()
            return

        self.log_dialog = LogViewerDialog(parent=self)
        self.log_dialog.show()
        self.log_dialog.raise_()
        self.log_dialog.activateWindow()

    def open_about(self):
        AboutDialog.open_AboutDialog(self)

    def reset_settings(self):
        confirm = CustomMessageBox.ask_yes_no(
            self,
            get("settings.reset.ask.title"),
            get("settings.reset.ask.message")
        )
        
        if confirm == "yes":
            
            self.txt_ws_url.clear()
            self.txt_mm_token.clear()
            self.txt_tg_token.clear()
            self.txt_tg_chat_id.clear()
            
            self.chk_echo.setChecked(True)
            self.toggle_anon.setChecked(False)
            self.toggle_sender.setChecked(True)
            self.toggle_channel.setChecked(True)
            self.toggle_message.setChecked(True)
            self.toggle_aes.setChecked(False)
            
            if os.path.exists(CONFIG_FILE_PATH):
                try:
                    os.remove(CONFIG_FILE_PATH)
                except Exception as e:
                    log.error(f"{get("log.settings.error_reset")} {e}")
            
            try:
                keyring.delete_password(APP_NAME, "MATTERMOST_TOKEN")
            except Exception:
                pass

            try:
                keyring.delete_password(APP_NAME, "TELEGRAM_BOT_TOKEN")
            except Exception:
                pass

            try:
                keyring.delete_password(APP_NAME, "AES_ENCRYPTION_KEY")
            except Exception:
                pass

            reset_settings()
            mattermost_listener.reconnect_websocket()
            load_language()

            self.on_top_window.setChecked(False)
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()

            if self.controller and hasattr(self.controller, "on_save_settings"):
                self.controller.on_save_settings()

            i18n_bridge.status_changed.emit("")
            CustomMessageBox.show_info(self, get("settings.reset.info.title"), get("settings.reset.info.message"))

    def update_theme(self):

        save_settings(
            config.get("MATTERMOST_WS_URL", ""),
            config.get("MATTERMOST_TOKEN", ""),
            config.get("TELEGRAM_BOT_TOKEN", ""),
            config.get("TELEGRAM_CHAT_ID", ""),
            config.get("EXCLUDED_SENDERS", ""),
            config.get("EXCLUDED_CHANNELS", ""),
            config.get("ECHO_SUPPRESSION_ENABLED", True),
            config.get("ANONYMOUS_MODE", False),
            config.get("INCLUDE_SENDER", True),
            config.get("INCLUDE_CHANNEL", True),
            config.get("INCLUDE_MESSAGE", True),
            config.get("AES_ENCRYPTION_ENABLED", False),
            config.get("ALWAYS_ON_TOP", False),
            config.get("WS_RECONNECT_TIMEOUT", 5),
            config.get("RETRY_LOGIC_TIMEOUT", 10),
            config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5),
            config.get("TG_HTTP_TIMEOUT", 5),
            config.get("LOG_LEVEL", "INFO"),
            "dark" if config.get("THEME", "light") == "light" else "light",
            config.get("LANGUAGE", get_system_locale())
        )

        if self.controller and hasattr(self.controller, "on_save_settings"):
            self.controller.on_save_settings()

    def save(self, showMessage=True):
        save_settings(
            self.txt_ws_url.text().strip(),
            self.txt_mm_token.text().strip(),
            self.txt_tg_token.text().strip(),
            self.txt_tg_chat_id.text().strip(),
            config.get("EXCLUDED_SENDERS", ""),
            config.get("EXCLUDED_CHANNELS", ""),
            self.chk_echo.isChecked(),
            self.toggle_anon.isChecked(),
            self.toggle_sender.isChecked(),
            self.toggle_channel.isChecked(),
            self.toggle_message.isChecked(),
            self.toggle_aes.isChecked(),
            self.on_top_window.isChecked(),
            config.get("WS_RECONNECT_TIMEOUT", 5),
            config.get("RETRY_LOGIC_TIMEOUT", 10),
            config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5),
            config.get("TG_HTTP_TIMEOUT", 5),
            config.get("LOG_LEVEL", "INFO"),
            config.get("THEME", "light"),
            config.get("LANGUAGE", get_system_locale())
        )

        if showMessage == True:
            mattermost_listener.reconnect_websocket()
            CustomMessageBox.show_info(self, get("settings.save.title"), get("settings.save.message"))

    def update_service_indicator_ui(self, checked):
        if checked == False:
            self.service_indicator.setStyleSheet("background-color: #adb5bd; border-radius: 5px;")
            self.service_indicator.setToolTip(get("settings.ui.marker_srv.inactive"))
        else:
            self.service_indicator.setStyleSheet("background-color: #00b4d8; border-radius: 5px;")
            self.service_indicator.setToolTip(get("settings.ui.marker_srv.active"))

    def update_ws_indicator_ui(self, is_connected: bool):
        if is_connected:
            self.ws_indicator.setStyleSheet("background-color: #009933; border-radius: 5px;")
            self.ws_indicator.setToolTip(get("settings.ui.marker_ws.connected"))
        else:
            self.ws_indicator.setStyleSheet("background-color: #e63946; border-radius: 5px;")
            self.ws_indicator.setToolTip(get("settings.ui.marker_ws.disconnected"))

    def closeEvent(self, event):

        current_values = {
            "MATTERMOST_WS_URL": self.txt_ws_url.text().strip(),
            "MATTERMOST_TOKEN": self.txt_mm_token.text().strip(),
            "TELEGRAM_CHAT_ID": self.txt_tg_chat_id.text().strip(),
            "TELEGRAM_BOT_TOKEN": self.txt_tg_token.text().strip(),
            "ECHO_SUPPRESSION_ENABLED": self.chk_echo.isChecked(),
            "ANONYMOUS_MODE": self.toggle_anon.isChecked(),
            "INCLUDE_SENDER": self.toggle_sender.isChecked(),
            "INCLUDE_CHANNEL": self.toggle_channel.isChecked(),
            "INCLUDE_MESSAGE": self.toggle_message.isChecked(),
            "AES_ENCRYPTION_ENABLED": self.toggle_aes.isChecked()
        }

        can_close = check_on_close(
            parent_window=self, 
            current_values=current_values, 
            save_callback=lambda: self.save(False)
        )

        if can_close:
            if self.log_dialog is not None and self.log_dialog.isVisible():
                self.log_dialog.close()
            event.accept()
        else:
            event.ignore()

    def reject(self):
        """
        Intercetta la chiusura tramite il tasto ESC (o chiamate di reject) 
        e la dirotta sul closeEvent per attivare il controllo delle modifiche.
        """
        self.close()

    def update_language(self):
        LanguageDialog.open_LanguageDialog(self)