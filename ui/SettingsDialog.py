import os
import keyring

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit,
    QFrame, QGroupBox, QVBoxLayout, QFileDialog
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from func.utils import resource_path
from func.aes import get_or_create_aes_key
from mattermost_listener import reconnect_websocket
from func.create_toggle_row import create_toggle_row
from settings import APP_NAME, CONFIG_FILE, config, save_settings, reset_settings

# --- FINESTRA IMPOSTAZIONI ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Mattermost Notifier")
        self.setFixedSize(450, 690)
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

        # Crittografia AES-256
        self.row_aes, self.toggle_aes = create_toggle_row("Crittografia Contenuto AES-256", "AES_ENCRYPTION_ENABLED", False)
        layout.addWidget(self.row_aes)

        # Checkbox Echo Suppression
        self.row_echo, self.chk_echo = create_toggle_row("Filtra automaticamente i miei messaggi (Echo Suppression)", "ECHO_SUPPRESSION_ENABLED")
        layout.addWidget(self.row_echo)

        # Checkbox modalità anonima
        self.row_anon, self.toggle_anon = create_toggle_row("Modalità Anonima (nascondi dettagli)", "ANONYMOUS_MODE")
        layout.addWidget(self.row_anon)

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

        # Pulsante per scaricare il decifratore HTML con la chiave pre-iniettata
        self.btn_download_decrypter = QPushButton("Scarica Decifratore HTML (AES-256)")
        self.btn_download_decrypter.setStyleSheet("background-color: #2b2d42; color: #f3f3f3;")
        self.btn_download_decrypter.clicked.connect(self.download_decrypter_html)
        layout.addWidget(self.btn_download_decrypter)

        self.setLayout(layout)

    def toggle_anonymous_mode(self, state):
        is_checked = (state == 2 or state is True)
        self.group_granular.setEnabled(not is_checked)

    def download_decrypter_html(self):

        # Recupera la chiave reale dell'utente (la genera se non esiste)
        user_key = get_or_create_aes_key()

        # Percorso del template decrypter.html originario (nella stessa cartella del progetto o risorse)
        template_path = resource_path(os.path.join("aes", "decrypter.html"))
        
        if not os.path.exists(template_path):
            QMessageBox.warning(self, "Attenzione", "File template 'decrypter.html' non trovato nella directory dell'applicazione.")
            return

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Sostituiamo la chiave di esempio nel file HTML con quella vera dell'utente
            chiave_esempio = "===MY_PRIVATE_KEY==="
            if chiave_esempio in html_content:
                html_content = html_content.replace(chiave_esempio, user_key)
            else:
                # Fallback di sicurezza nel caso l'input avesse un ID diverso nel tag HTML
                # Cerchiamo l'input value o iniettiamo direttamente via stringa
                pass

            # Chiediamo all'utente dove salvare il file personalizzato
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva Decifratore AES",
                "decrypter_personale.html",
                "File HTML (*.html)"
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                QMessageBox.information(self, "Download Completato", f"Il decifratore personalizzato è stato salvato con successo in:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile generare il file di decifrazione: {e}")

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
            self.toggle_aes.setChecked(False)
            
            # Cancelliamo fisicamente il file di configurazione se esiste
            if os.path.exists(CONFIG_FILE):
                try:
                    os.remove(CONFIG_FILE)
                except Exception as e:
                    print(f"Errore rimozione file config: {e}")
            
            # Rimuoviamo anche i token dal keyring di sistema
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
            self.toggle_message.isChecked(),
            self.toggle_aes.isChecked()
        )

        reconnect_websocket()

        QMessageBox.information(self, "Salvato", "Le impostazioni sono state salvate!")
        #self.accept()