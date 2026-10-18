import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QMessageBox, 
    QSpinBox, QPushButton, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from func.utils import resource_path
from settings import config, save_settings
from func.check_on_close import check_on_close

class TimeoutSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Impostazioni Timeout & Retry")
        self.setFixedSize(380, 220)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))
        
        layout = QVBoxLayout(self)

        group_box = QGroupBox("Configurazione Intervalli")
        form_layout = QFormLayout(group_box)

        # 1. Timeout Listener WebSocket
        self.ws_timeout_spin = QSpinBox()
        self.ws_timeout_spin.setRange(1, 300)
        self.ws_timeout_spin.setSuffix(" s")
        # Recupa il valore attuale dalla config (default es. 5s)
        self.ws_timeout_spin.setValue(int(config.get("WS_RECONNECT_TIMEOUT", 5)))
        form_layout.addRow("Timeout Riconnessione:", self.ws_timeout_spin)

        # 2. Timeout Retry Logic (Coda di invio)
        self.retry_timeout_spin = QSpinBox()
        self.retry_timeout_spin.setRange(1, 300)
        self.retry_timeout_spin.setSuffix(" s")
        # Recupa il valore attuale dalla config (default es. 10s)
        self.retry_timeout_spin.setValue(int(config.get("RETRY_LOGIC_TIMEOUT", 10)))
        form_layout.addRow("Timeout Retry Logic:", self.retry_timeout_spin)

        # 3. Max Tentativi
        self.max_attempts_spin = QSpinBox()
        self.max_attempts_spin.setRange(1, 50)
        self.max_attempts_spin.setValue(int(config.get("RETRY_LOGIC_MAX_ATTEMPTS", 5)))
        form_layout.addRow("Max Tentativi Retry:", self.max_attempts_spin)

        # 4. Timeout http client telegram
        self.timeout_http_tg = QSpinBox()
        self.timeout_http_tg.setRange(1, 300)
        self.timeout_http_tg.setSuffix(" s")
        self.timeout_http_tg.setValue(int(config.get("TG_HTTP_TIMEOUT", 5)))
        form_layout.addRow("Timeout HTTP Telegram:", self.timeout_http_tg)

        layout.addWidget(group_box)

        # Pulsanti Salva / Annulla
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annulla")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Salva")
        self.btn_save.setStyleSheet("background-color: #007acc; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(lambda: self.save_settings())
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

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
            config.get("LOG_LEVEL", "INFO")
        )

        if showMessage == True:
            QMessageBox.information(self, "Salvato", "La lista è stata aggiornata con successo!")

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