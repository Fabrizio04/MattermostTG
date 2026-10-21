from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout,
    QTextEdit, QPushButton, QWidget
)

from settings import config, save_settings

from ui.CustomTitleBar import CustomTitleBar
from ui.CustomMessageBox import CustomMessageBox

from func.i18n import get
from func.check_on_close import check_on_close
from func.get_system_locale import get_system_locale
from func.window import initialize_window, exec_with_parent_dim

class ExcludedListDialog(QDialog):
    def __init__(self, list_type: str, parent=None):
        super().__init__(parent)
        self.list_type = list_type  # "senders" o "channels"
        
        # Configuriamo etichette e chiavi in base al tipo
        if self.list_type == "senders":
            self.title_text = get("excludedlist.senders.title_text")
            self.label_text = get("excludedlist.senders.label_text")
            self.config_key = "EXCLUDED_SENDERS"
        else:
            self.title_text = get("excludedlist.channels.title_text")
            self.label_text = get("excludedlist.channels.label_text")
            self.config_key = "EXCLUDED_CHANNELS"

        initialize_window(self, 400, 300)

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
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)

        # Etichetta descrittiva
        layout.addWidget(QLabel(self.label_text))

        # Textarea
        self.text_area = QTextEdit()
        self.text_area.setText(config.get(self.config_key, ""))
        layout.addWidget(self.text_area)

        # Pulsanti Salva / Annulla
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton(get("main.cancel"))
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton(get("main.save"))
        self.btn_save.clicked.connect(lambda: self.save_list())
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

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
            config.get("THEME", "light"),
            config.get("LANGUAGE", get_system_locale())
        )

        if showMessage == True:
            CustomMessageBox.show_info(self, get("excludedlist.alert_title"), get("excludedlist.alert_message"))

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
        exec_with_parent_dim(dlg, parent)