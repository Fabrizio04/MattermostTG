import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout,
    QTextEdit, QPushButton, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon
from func.utils import resource_path
from settings import config, save_settings
from func.check_on_close import check_on_close

from ui.CustomTitleBar import CustomTitleBar
from ui.DimmerOverlay import DimmerOverlay
from ui.CustomMessageBox import CustomMessageBox

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

        #self.setWindowTitle(self.title_text)
        self.setFixedSize(400, 300)
        ###
        # --- EFFETTO FADE-IN (COMPARSA SFUMATA) ---
        self.setWindowOpacity(0.0) # Parte completamente trasparente
        
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200) # Durata in millisecondi (es. 0.2 secondi)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Avvia l'animazione appena la finestra viene creata
        self.fade_animation.start()
        ###

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        if config.get("ALWAYS_ON_TOP", False) == True:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title=self.title_text)
        container_layout.addWidget(self.title_bar)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 15) # Left, Top, Right, Bottom
        layout.setSpacing(10) # Spazio verticale costante tra i blocchi

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
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Salva")
        #self.btn_save.setStyleSheet("background-color: #007acc; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(lambda: self.save_list())
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        # self.setLayout(layout)

    def save_list(self, showMessage=True):
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
            config.get("LOG_LEVEL", "INFO"),
            config.get("THEME", "light")
        )

        if showMessage == True:
            CustomMessageBox.show_info(self, "Salvato", "La lista è stata aggiornata con successo!")
            # QMessageBox.information(self, "Salvato", "La lista è stata aggiornata con successo!")

        self.accept()

    def closeEvent(self, event):

        current_values = {
            self.config_key: self.text_area.toPlainText().strip()
        }

        can_close = check_on_close(
            parent_window=self, 
            current_values=current_values, 
            save_callback=lambda: self.save_list(False)
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
    def open_ExcludedListDialog(list_type, parent):
        dlg = ExcludedListDialog(list_type = list_type, parent=parent)
        #dlg.exec()
        ExcludedListDialog._exec_with_parent_dim(dlg, parent)

    @staticmethod
    def _exec_with_parent_dim(dlg, parent):
        overlay = None
        if parent:
            current_theme = config.get("THEME", "light")
            
            if current_theme == "dark":
                # Nero semitrasparente per il tema scuro
                rgba_css = "rgba(0, 0, 0, 130)"
            else:
                # Nero più marcato (circa al 50-60% di opacità) per spegnere il bianco del tema chiaro
                rgba_css = "rgba(0, 0, 0, 150)"
                
            overlay = DimmerOverlay(parent, rgba_css)
            overlay.show()

        try:
            dlg.exec()
        finally:
            if overlay:
                overlay.deleteLater()