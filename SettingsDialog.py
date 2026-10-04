from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)

from PyQt6.QtCore import Qt
from settings import config, save_settings
from listen_mattermost import reconnect_websocket 

# --- FINESTRA IMPOSTAZIONI ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Mattermost Notifier")
        self.setFixedSize(450, 240)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # WS URL
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Mattermost WS URL:"))
        self.txt_ws_url = QLineEdit(config.get("MATTERMOST_WS_URL", ""))
        h1.addWidget(self.txt_ws_url)
        layout.addLayout(h1)

        # MM Token
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Mattermost Token:"))
        self.txt_mm_token = QLineEdit(config.get("MATTERMOST_TOKEN", ""))
        self.txt_mm_token.setEchoMode(QLineEdit.EchoMode.Password)
        h2.addWidget(self.txt_mm_token)
        layout.addLayout(h2)

        # TG Token
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Telegram Bot Token:"))
        self.txt_tg_token = QLineEdit(config.get("TELEGRAM_BOT_TOKEN", ""))
        self.txt_tg_token.setEchoMode(QLineEdit.EchoMode.Password)
        h3.addWidget(self.txt_tg_token)
        layout.addLayout(h3)

        # TG Chat ID
        h4 = QHBoxLayout()
        h4.addWidget(QLabel("Telegram Chat ID:"))
        self.txt_tg_chat_id = QLineEdit(config.get("TELEGRAM_CHAT_ID", ""))
        h4.addWidget(self.txt_tg_chat_id)
        layout.addLayout(h4)

        # Bottone Salva
        self.btn_save = QPushButton("Salva Impostazioni")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    def save(self):
        save_settings(
            self.txt_ws_url.text().strip(),
            self.txt_mm_token.text().strip(),
            self.txt_tg_token.text().strip(),
            self.txt_tg_chat_id.text().strip()
        )

        reconnect_websocket()

        QMessageBox.information(self, "Salvato", "Le impostazioni sono state salvate!")
        self.accept()