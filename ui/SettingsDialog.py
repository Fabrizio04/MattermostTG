import os
import shutil
import keyring
import mattermost_listener

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox,
    QVBoxLayout, QFileDialog, QMenuBar,
    QGridLayout, QWidget, QHBoxLayout
)

from PyQt6.QtCore import Qt
from func.utils import resource_path
from PyQt6.QtGui import QIcon, QAction
from ui.AboutDialog import AboutDialog
from ui.WSStatusBridge import ws_bridge
from func.aes import get_or_create_aes_key
from func.create_toggle_row import create_toggle_row
from ui.ExcludedListDialog import ExcludedListDialog
from settings import APP_NAME, CONFIG_FILE, config, save_settings, reset_settings

# --- FINESTRA IMPOSTAZIONI ---
class SettingsDialog(QDialog):
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller

        self.setWindowTitle("Impostazioni Mattermost Notifier")
        self.setFixedSize(450, 470)

        if config.get("ALWAYS_ON_TOP", False) == True:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))

        self.menu_bar = QMenuBar(self)
        # Aggiungiamo un tocco di stile per separarla visivamente dal contenuto
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #d1d5db;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #e5e7eb;
            }
        """)

        # --- MENU FILE ---
        menu_file = self.menu_bar.addMenu("File")
        
        act_import = QAction("Importa impostazioni da JSON", self)
        act_import.triggered.connect(self.import_settings_json)
        menu_file.addAction(act_import)
        
        act_export = QAction("Esporta impostazioni in JSON", self)
        act_export.triggered.connect(self.export_settings_json)
        menu_file.addAction(act_export)
        
        menu_file.addSeparator()
        
        act_exit = QAction("Esci", self)
        act_exit.triggered.connect(self.close)
        menu_file.addAction(act_exit)

        # --- MENU MODIFICA ---
        menu_edit = self.menu_bar.addMenu("Modifica")
        
        self.act_notif = QAction("Notifiche attive", self) # Da collegare o gestire come toggle
        self.act_notif.setCheckable(True)
        self.act_notif.triggered.connect(self.toggle_notifications_from_menu)
        self.act_notif.setChecked(mattermost_listener.service_active)
        menu_edit.addAction(self.act_notif)
        
        act_senders = QAction("Mittenti da scartare...", self)
        act_senders.triggered.connect(lambda: self.open_excluded_dialog("senders"))
        menu_edit.addAction(act_senders)
        
        act_channels = QAction("Canali da scartare...", self)
        act_channels.triggered.connect(lambda: self.open_excluded_dialog("channels"))
        menu_edit.addAction(act_channels)
        
        menu_edit.addSeparator()
        
        act_reset = QAction("Ripristina impostazioni predefinite", self)
        act_reset.triggered.connect(self.reset_settings)
        menu_edit.addAction(act_reset)

        # --- MENU VISUALIZZA ---
        menu_view = self.menu_bar.addMenu("Visualizza")

        self.on_top_window = QAction("Finestra in primo piano", self)
        self.on_top_window.setCheckable(True)
        self.on_top_window.triggered.connect(self.update_on_top_window)
        self.on_top_window.setChecked(config.get("ALWAYS_ON_TOP", False))
        menu_view.addAction(self.on_top_window)

        theme = QAction("Tema (chiaro / scuro)", self)
        menu_view.addAction(theme)

        language = QAction("Lingua", self)
        menu_view.addAction(language)

        # --- MENU AVANZATE ---
        menu_advanced = self.menu_bar.addMenu("Avanzate")
        
        act_timeout_listener = QAction("Impostazione timeout listener", self)
        menu_advanced.addAction(act_timeout_listener)
        
        act_timeout_retry = QAction("Impostazione timeout retry logic", self)
        menu_advanced.addAction(act_timeout_retry)
        
        act_debug = QAction("Impostazione livello debug", self)
        menu_advanced.addAction(act_debug)
        
        act_logs = QAction("Log applicazione", self)
        menu_advanced.addAction(act_logs)

        # --- MENU AES-256 ---
        menu_aes = self.menu_bar.addMenu("Aes-256")
        
        act_regen_key = QAction("Rigenerazione chiave privata Aes-256", self)
        act_regen_key.triggered.connect(self.regenerate_aes_key)
        menu_aes.addAction(act_regen_key)
        
        act_download_key = QAction("Download chiave privata", self)
        act_download_key.triggered.connect(self.download_raw_key)
        menu_aes.addAction(act_download_key)
        
        act_download_dec = QAction("Download decrypter html", self)
        act_download_dec.triggered.connect(lambda: self.download_decrypter_html(False))
        menu_aes.addAction(act_download_dec)
        
        act_download_dec_key = QAction("Download decrypter html + chiave", self)
        act_download_dec_key.triggered.connect(lambda: self.download_decrypter_html(True))
        menu_aes.addAction(act_download_dec_key)

        # --- MENU AIUTO ---
        menu_help = self.menu_bar.addMenu("Aiuto")
        
        act_updates = QAction("Verifica aggiornamenti", self)
        menu_help.addAction(act_updates)
        
        act_about = QAction("Informazioni", self)
        act_about.triggered.connect(self.open_about)
        menu_help.addAction(act_about)

        # Stati connessione
        status_container = QWidget()
        status_container.setFixedHeight(24)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 10, 0) # Un po' di margine a destra
        status_layout.setSpacing(6)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # status_container.setStyleSheet("margin-top: 4px;")

        # Indicatore 1: Stato Websocket (es. Rosso = disconnesso, Verde = connesso)
        self.ws_indicator = QLabel()
        self.ws_indicator.setFixedSize(10, 10)
        self.ws_indicator.setStyleSheet("background-color: #e63946; border-radius: 5px;") # Rosso iniziale
        self.ws_indicator.setToolTip("Stato WebSocket: Disconnesso")

        # Indicatore 2: Stato Servizio (es. Grigio = fermo, Azzurro/Verde = attivo)
        self.service_indicator = QLabel()
        self.service_indicator.setFixedSize(10, 10)
        self.service_indicator.setStyleSheet("background-color: #adb5bd; border-radius: 5px;") # Grigio iniziale
        self.service_indicator.setToolTip("Stato Servizio: Fermo")

        # Aggiungiamo al layout
        status_layout.addWidget(self.ws_indicator)
        status_layout.addWidget(self.service_indicator)

        # Posizioniamo il tutto nell'angolo in alto a destra della menu bar
        self.menu_bar.setCornerWidget(status_container, Qt.Corner.TopRightCorner)

        # Layout principale in cui inseriamo la menu bar in cima
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar) # Imposta la barra dei menu in alto

        layout = QVBoxLayout()

        # WS URL
        self.txt_ws_url = QLineEdit(config.get("MATTERMOST_WS_URL", ""))
        self.txt_ws_url.setPlaceholderText("wss://mattermost.tuodominio.it/api/v4/websocket")

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

        # Usiamo un QGridLayout per allineare perfettamente etichette e input
        grid_layout = QGridLayout()
        
        labels_texts = [
            ("Mattermost WS URL:", self.txt_ws_url),
            ("Mattermost Token:", self.txt_mm_token),
            ("Telegram Bot Token:", self.txt_tg_token),
            ("Telegram Chat ID:", self.txt_tg_chat_id)
        ]

        for row, (label_text, line_edit) in enumerate(labels_texts):
            lbl = QLabel(label_text)
            # Fissiamo una larghezza minima o fissa per le label così l'inizio delle caselle è perfettamente verticale
            lbl.setFixedWidth(130) 
            grid_layout.addWidget(lbl, row, 0)
            
            # Impostiamo una dimensione omogenea o lasciamo che occupino lo spazio uniformemente
            line_edit.setMinimumWidth(260)
            grid_layout.addWidget(line_edit, row, 1)

        layout.addLayout(grid_layout)

        # Crittografia AES-256
        self.row_aes, self.toggle_aes = create_toggle_row("Crittografia Contenuto AES-256", "AES_ENCRYPTION_ENABLED", False)
        layout.addWidget(self.row_aes)

        # Checkbox Echo Suppression
        self.row_echo, self.chk_echo = create_toggle_row("Filtra automaticamente i miei messaggi (Echo Suppression)", "ECHO_SUPPRESSION_ENABLED")
        layout.addWidget(self.row_echo)

        # Checkbox modalità anonima
        self.row_anon, self.toggle_anon = create_toggle_row("Modalità Anonima (nascondi dettagli)", "ANONYMOUS_MODE")
        self.toggle_anon.stateChanged.connect(lambda state: self.toggle_anonymous_mode(state))
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

        # Bottone Salva
        self.btn_save = QPushButton("Salva Modifiche")
        #self.btn_save.setStyleSheet("background-color: #00b4d8; color: #f3f3f3;")
        self.btn_save.setStyleSheet("background-color: #00b4d8; color: #f3f3f3; padding: 8px; font-weight: bold;")
        self.btn_save.clicked.connect(lambda: self.save())
        layout.addWidget(self.btn_save)

        # self.setLayout(layout)
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

        ws_bridge.status_changed.connect(self.update_ws_indicator_ui)
        self.update_ws_indicator_ui(mattermost_listener.is_websocket_connected())
        self.update_service_indicator_ui(mattermost_listener.service_active)

    def export_settings_json(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Esporta Impostazioni", "mattermosttg_settings.json", "JSON Files (*.json)")
        if file_path:
            try:
                if os.path.exists(CONFIG_FILE):
                    shutil.copy(CONFIG_FILE, file_path)
                    QMessageBox.information(self, "Esportazione", "Impostazioni esportate con successo!")
                else:
                    QMessageBox.warning(self, "Attenzione", "File di configurazione non trovato.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile esportare: {e}")

    def import_settings_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importa Impostazioni", "", "JSON Files (*.json)")
        if file_path:
            try:
                shutil.copy(file_path, CONFIG_FILE)
                from settings import load_settings # O ricarica config
                load_settings()
                #ricaricare la UI...
                QMessageBox.information(self, "Importazione", "Impostazioni importate! Riavvia la finestra per vedere le modifiche.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile importare: {e}")

    def regenerate_aes_key(self):
        confirm = QMessageBox.question(self, "Rigenera Chiave", "Rigenerare la chiave invaliderà i messaggi cifrati precedenti con la chiave vecchia. Continuare?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                try:
                    keyring.delete_password(APP_NAME, "AES_ENCRYPTION_KEY")
                except Exception:
                    pass
                get_or_create_aes_key()
                QMessageBox.information(self, "Chiave Rigenerata", "La nuova chiave AES-256 è stata generata e salvata nel keyring.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore nella rigenerazione: {e}")

    def download_raw_key(self):
        user_key = get_or_create_aes_key()
        file_path, _ = QFileDialog.getSaveFileName(self, "Salva Chiave AES", "chiave_aes.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(user_key)
            QMessageBox.information(self, "Download", "Chiave salvata con successo!")

    def toggle_anonymous_mode(self, state):
        is_checked = (state == 2 or state is True)
        self.group_granular.setEnabled(not is_checked)

    def download_decrypter_html(self, includeKey):

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
                html_content = html_content.replace(chiave_esempio, get_or_create_aes_key() if includeKey == True else "")
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
        self.show()  # Fondamentale per applicare il cambio flag a caldo!
        self.save(False)

    def open_excluded_dialog(self, list_type):
        dialog = ExcludedListDialog(list_type, self)
        dialog.exec()

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

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
            mattermost_listener.reconnect_websocket()

            self.on_top_window.setChecked(False)
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            
            # Notifica visiva all'utente
            QMessageBox.information(self, "Reset Completato", "Le impostazioni sono state ripristinate con successo.")

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
            self.on_top_window.isChecked()
        )

        if showMessage == True:
            mattermost_listener.reconnect_websocket()
            QMessageBox.information(self, "Salvato", "Le impostazioni sono state salvate!")
        
        #self.accept()

    def update_service_indicator_ui(self, checked):
        if checked == False:
            self.service_indicator.setStyleSheet("background-color: #adb5bd; border-radius: 5px;") # Grigio iniziale
            self.service_indicator.setToolTip("Stato Servizio: Fermo")
        else:
            self.service_indicator.setStyleSheet("background-color: #00b4d8; border-radius: 5px;")
            self.service_indicator.setToolTip("Stato Servizio: Attivo") 

    def update_ws_indicator_ui(self, is_connected: bool):
        if is_connected:
            self.ws_indicator.setStyleSheet("background-color: #009933; border-radius: 5px;")
            self.ws_indicator.setToolTip("Stato WebSocket: Connesso")
        else:
            self.ws_indicator.setStyleSheet("background-color: #e63946; border-radius: 5px;")
            self.ws_indicator.setToolTip("Stato WebSocket: Disconnesso")

    def closeEvent(self, event):
        event.accept()
        super().closeEvent(event)