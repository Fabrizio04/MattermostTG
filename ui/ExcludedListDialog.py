import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout,
    QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from func.utils import resource_path
from settings import config, save_settings

class ExcludedListDialog(QDialog):
    def __init__(self, list_type: str, parent=None):
        super().__init__(parent)
        self.list_type = list_type  # "senders" o "channels"
        
        # Configuriamo etichette e chiavi in base al tipo
        if self.list_type == "senders":
            self.title_text = "Gestione Mittenti da Scartare"
            self.label_text = "Mittenti da scartare (uno per riga o separati da virgola):"
            self.config_key = "EXCLUDED_SENDERS"
        else:
            self.title_text = "Gestione Canali da Scartare"
            self.label_text = "Canali da scartare (uno per riga o separati da virgola):"
            self.config_key = "EXCLUDED_CHANNELS"

        self.setWindowTitle(self.title_text)
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))

        layout = QVBoxLayout()

        # Etichetta descrittiva
        layout.addWidget(QLabel(self.label_text))

        # Textarea
        self.text_area = QTextEdit()
        self.text_area.setText(config.get(self.config_key, ""))
        layout.addWidget(self.text_area)

        # Pulsanti Salva / Annulla
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Annulla")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Salva")
        self.btn_save.setStyleSheet("background-color: #007acc; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_list)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_list(self):
        content = self.text_area.toPlainText().strip()
        
        save_settings(
            config.get("MATTERMOST_WS_URL", ""),
            config.get("MATTERMOST_TOKEN", ""),
            config.get("TELEGRAM_BOT_TOKEN", ""),
            config.get("TELEGRAM_CHAT_ID", ""),
            content if self.list_type == "senders" else config.get("EXCLUDED_SENDERS", ""),
            content if self.list_type == "channels" else config.get("EXCLUDED_CHANNELS", ""),
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
            config.get("LOG_LEVEL", "INFO")
        )
        
        QMessageBox.information(self, "Salvato", "La lista è stata aggiornata con successo!")
        self.accept()