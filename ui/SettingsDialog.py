import os
import keyring

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit,
    QFrame, QGroupBox, QVBoxLayout
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from func.utils import resource_path
from ui.ToggleSwitch import ToggleSwitch
from listen_mattermost import reconnect_websocket
from func.create_toggle_row import create_toggle_row
from settings import APP_NAME, CONFIG_FILE, config, save_settings

# --- FINESTRA IMPOSTAZIONI ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Mattermost Notifier")
        self.setFixedSize(450, 610)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))

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

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Esclusione Mittenti
        layout.addWidget(QLabel("Mittenti da scartare (uno per riga o separati da virgola):"))
        self.txt_excluded_senders = QTextEdit()
        self.txt_excluded_senders.setMaximumHeight(60)
        self.txt_excluded_senders.setText(config.get("EXCLUDED_SENDERS", ""))
        layout.addWidget(self.txt_excluded_senders)

        # Esclusione Canali
        layout.addWidget(QLabel("Canali da scartare (uno per riga o separati da virgola):"))
        self.txt_excluded_channels = QTextEdit()
        self.txt_excluded_channels.setMaximumHeight(60)
        self.txt_excluded_channels.setText(config.get("EXCLUDED_CHANNELS", ""))
        layout.addWidget(self.txt_excluded_channels)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Checkbox Echo Suppression
        # self.chk_echo = QCheckBox("Filtra automaticamente i miei messaggi (Echo Suppression)")
        # self.chk_echo.setChecked(config.get("ECHO_SUPPRESSION_ENABLED", True))
        # layout.addWidget(self.chk_echo)
        h_echo = QHBoxLayout()
        lbl_echo = QLabel("Filtra automaticamente i miei messaggi (Echo Suppression):")
        self.chk_echo = ToggleSwitch()
        self.chk_echo.setChecked(config.get("ECHO_SUPPRESSION_ENABLED", True))
        
        h_echo.addWidget(lbl_echo)
        h_echo.addStretch()  # Spinge il toggle a destra
        h_echo.addWidget(self.chk_echo)
        layout.addLayout(h_echo)

        # Checkbox modalità anonima
        h_anon = QHBoxLayout()
        lbl_anon = QLabel("Modalità Anonima (nascondi dettagli):")
        self.toggle_anon = ToggleSwitch()
        self.toggle_anon.setChecked(config.get("ANONYMOUS_MODE", False))

        # Colleghiamo il segnale per disabilitare/abilitare i campi sottostanti
        self.toggle_anon.stateChanged.connect(self.toggle_anonymous_mode)

        h_anon.addWidget(lbl_anon)
        h_anon.addStretch()
        h_anon.addWidget(self.toggle_anon)
        layout.addLayout(h_anon)

        # GroupBox per i campi granulari (attivi se Anonimo è disattivato)
        self.group_granular = QGroupBox("Campi da includere nelle notifiche:")
        vbox_granular = QVBoxLayout()

        # Canale, Mittente e Messaggio
        self.row_channel, self.toggle_channel = create_toggle_row("Includi Canale", "INCLUDE_CHANNEL")
        self.row_sender, self.toggle_sender = create_toggle_row("Includi Mittente", "INCLUDE_SENDER") 
        self.row_message, self.toggle_message = create_toggle_row("Includi Contenuto Messaggio", "INCLUDE_MESSAGE")
        
        vbox_granular.addWidget(self.row_channel)
        vbox_granular.addWidget(self.row_sender)
        vbox_granular.addWidget(self.row_message)

        self.group_granular.setLayout(vbox_granular)
        layout.addWidget(self.group_granular)
        self.toggle_anonymous_mode(self.toggle_anon.isChecked())

        # HR
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Bottone Salva
        self.btn_save = QPushButton("Salva Impostazioni")
        self.btn_save.setStyleSheet("background-color: #00b4d8; color: #f3f3f3;")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

        # Pulsante Reset
        self.btn_reset = QPushButton("Ripristina Predefiniti")
        self.btn_reset.setStyleSheet("background-color: #fc473a; color: #f3f3f3;")
        self.btn_reset.clicked.connect(self.reset_settings)
        layout.addWidget(self.btn_reset)

        self.setLayout(layout)

    def toggle_anonymous_mode(self, state):
        is_checked = (state == 2 or state is True)
        self.group_granular.setEnabled(not is_checked)

    def reset_settings(self):
        # Chiediamo conferma prima di resettare
        confirm = QMessageBox.question(
            self,
            "Conferma Reset",
            "Sei sicuro di voler ripristinare le impostazioni predefinite?\nTutti i campi e i token salvati verranno cancellati.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Pulisciamo i campi di testo
            self.txt_ws_url.clear()
            self.txt_mm_token.clear()
            self.txt_tg_token.clear()
            self.txt_tg_chat_id.clear()
            self.txt_excluded_senders.clear()
            self.txt_excluded_channels.clear()
            
            # Riportiamo i toggle allo stato predefinito
            self.chk_echo.setChecked(True)
            self.toggle_anon.setChecked(False)
            self.toggle_sender.setChecked(True)
            self.toggle_channel.setChecked(True)
            self.toggle_message.setChecked(True)
            
            # Cancelliamo fisicamente il file di configurazione se esiste
            if os.path.exists(CONFIG_FILE):
                try:
                    os.remove(CONFIG_FILE)
                except Exception as e:
                    print(f"Errore rimozione file config: {e}")
            
            # Rimuoviamo anche i token dal keyring di sistema
            try:
                keyring.delete_password(APP_NAME, "MATTERMOST_TOKEN")
                keyring.delete_password(APP_NAME, "TELEGRAM_BOT_TOKEN")
            except Exception:
                pass  # Se non esistono nel keyring, ignoriamo l'eccezione

            # Notifica visiva all'utente
            QMessageBox.information(self, "Reset Completato", "Le impostazioni sono state ripristinate con successo.")

    def save(self):
        save_settings(
            self.txt_ws_url.text().strip(),
            self.txt_mm_token.text().strip(),
            self.txt_tg_token.text().strip(),
            self.txt_tg_chat_id.text().strip(),
            self.txt_excluded_senders.toPlainText().strip(),
            self.txt_excluded_channels.toPlainText().strip(),
            self.chk_echo.isChecked(),
            self.toggle_anon.isChecked(),
            self.toggle_sender.isChecked(),
            self.toggle_channel.isChecked(),
            self.toggle_message.isChecked()
        )

        reconnect_websocket()

        QMessageBox.information(self, "Salvato", "Le impostazioni sono state salvate!")
        #self.accept()