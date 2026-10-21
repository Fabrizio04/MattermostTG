from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpinBox, QPushButton, QFormLayout, QGroupBox,
)

from ui.CustomTitleBar import CustomTitleBar
from ui.CustomMessageBox import CustomMessageBox

from func.i18n import get
from func.check_on_close import check_on_close
from func.theme import DARK_THEME, LIGHT_THEME
from func.get_system_locale import get_system_locale
from func.window import initialize_window, exec_with_parent_dim

from settings import config, save_settings

class TimeoutSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        initialize_window(self, 380, 260)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title=get("timeout.title"))
        container_layout.addWidget(self.title_bar)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 15) # Left, Top, Right, Bottom
        layout.setSpacing(10) # Spazio verticale costante tra i blocchi

        theme = DARK_THEME if config.get("THEME", "light") == "dark" else LIGHT_THEME

        group_box = QGroupBox(get("timeout.group_box"))
        form_layout = QFormLayout(group_box)

        # Timeout Listener WebSocket
        self.ws_timeout_spin = QSpinBox()
        self.ws_timeout_spin.setStyleSheet(f"background-color: {theme["input_bg"]};color: {theme["input_fg"]};")
        self.ws_timeout_spin.setRange(1, 300)
        self.ws_timeout_spin.setSuffix(" s")
        self.ws_timeout_spin.setValue(int(config.get("WS_RECONNECT_TIMEOUT", 5)))
        form_layout.addRow(get("timeout.field1"), self.ws_timeout_spin)

        # Timeout Retry Logic (Coda di invio)
        self.retry_timeout_spin = QSpinBox()
        self.retry_timeout_spin.setStyleSheet(f"background-color: {theme["input_bg"]};color: {theme["input_fg"]};")
        self.retry_timeout_spin.setRange(1, 300)
        self.retry_timeout_spin.setSuffix(" s")
        self.retry_timeout_spin.setValue(int(config.get("RETRY_LOGIC_TIMEOUT", 10)))
        form_layout.addRow(get("timeout.field2"), self.retry_timeout_spin)

        # Max Tentativi
        self.max_attempts_spin = QSpinBox()
        self.max_attempts_spin.setStyleSheet(f"background-color: {theme["input_bg"]};color: {theme["input_fg"]};")
        self.max_attempts_spin.setRange(1, 50)
        self.max_attempts_spin.setValue(int(config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5)))
        form_layout.addRow(get("timeout.field3"), self.max_attempts_spin)

        # Timeout http client telegram
        self.timeout_http_tg = QSpinBox()
        self.timeout_http_tg.setStyleSheet(f"background-color: {theme["input_bg"]};color: {theme["input_fg"]};")
        self.timeout_http_tg.setRange(1, 300)
        self.timeout_http_tg.setSuffix(" s")
        self.timeout_http_tg.setValue(int(config.get("TG_HTTP_TIMEOUT", 5)))
        form_layout.addRow(get("timeout.field4"), self.timeout_http_tg)

        layout.addWidget(group_box)

        # Pulsanti Salva / Annulla
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton(get("main.cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton(get("main.save"))
        self.btn_save.clicked.connect(lambda: self.save_settings())
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def save_settings(self, showMessage=True):
        ws_val = self.ws_timeout_spin.value()
        retry_val = self.retry_timeout_spin.value()
        attempts_val = self.max_attempts_spin.value()
        tg_http_val = self.timeout_http_tg.value()

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
            ws_val,
            retry_val,
            attempts_val,
            tg_http_val,
            config.get("LOG_LEVEL", "INFO"),
            config.get("THEME", "light"),
            config.get("LANGUAGE", get_system_locale())
        )

        if showMessage == True:
            CustomMessageBox.show_info(self, get("timeout.alert_title"), get("timeout.alert_message"))

        self.accept()

    def closeEvent(self, event):
    
        current_values = {
            "WS_RECONNECT_TIMEOUT": self.ws_timeout_spin.value(),
            "RETRY_LOGIC_TIMEOUT": self.retry_timeout_spin.value(),
            "RETRY_LOGIC_MAX_ATTEMPTS": self.max_attempts_spin.value(),
            "TG_HTTP_TIMEOUT": self.timeout_http_tg.value(),
        }

        can_close = check_on_close(
            parent_window=self, 
            current_values=current_values, 
            save_callback=lambda: self.save_settings(False)
        )

        if can_close:
            event.accept()
        else:
            event.ignore()

    def reject(self):
        """
        Intercetta la chiusura tramite il tasto ESC (o chiamate di reject) 
        e la dirotta sul closeEvent per attivare il controllo delle modifiche.
        """
        self.close()

    @staticmethod
    def open_TimeoutSettingsDialog(parent):
        dlg = TimeoutSettingsDialog(parent=parent)
        exec_with_parent_dim(dlg, parent)