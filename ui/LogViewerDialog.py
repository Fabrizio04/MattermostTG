import os
import logging

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QGuiApplication, QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QWidget, QComboBox, QPushButton, QTextEdit
)

from logger import log, LOG_FILE_PATH
from settings import config, save_settings

from ui.LangStatusBridge import i18n_bridge
from ui.CustomTitleBar import CustomTitleBar
from ui.CustomMessageBox import CustomMessageBox

from func.i18n import get
from func.utils import resource_path
from func.window import fade_animation
from func.get_system_locale import get_system_locale

class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(850, 470)
        fade_animation(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowIcon(QIcon(resource_path(os.path.join("img", "icon_active.png"))))
        
        self.last_file_pos = 0

        if parent:
            # Usiamo frameGeometry() per includere i bordi/barra del titolo reali della finestra
            parent_geo = parent.frameGeometry()
            screen_geo = QGuiApplication.primaryScreen().availableGeometry()

            # Forziamo la stessa altezza del parent (inclusa la cornice)
            self.resize(self.width(), parent_geo.height())

            # Calcoliamo la coordinata X a destra del parent + 10px di margine
            new_x = parent_geo.x() + parent_geo.width() + 10
            # Allineiamo la Y esattamente alla stessa altezza del bordo superiore del parent
            new_y = parent_geo.y()

            # Se la finestra esce dallo schermo a destra, la posizioniamo a sinistra del parent
            if new_x + self.width() > screen_geo.right():
                new_x = parent_geo.x() - self.width() - 10

            # Controlli di sicurezza per non uscire dai bordi dello schermo
            new_x = max(screen_geo.left(), min(new_x, screen_geo.right() - self.width()))
            new_y = max(screen_geo.top(), min(new_y, screen_geo.bottom() - self.height()))

            self.move(new_x, new_y)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title=get("logviewer.title"))
        container_layout.addWidget(self.title_bar)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)

        # --- BARRA SUPERIORE CONTROLLI --- #
        top_layout = QHBoxLayout()

        self.logging_level = QLabel(get("logviewer.logging_level"))
        top_layout.addWidget(self.logging_level)

        self.combo_level = QComboBox()
        self.combo_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        
        current_level = config.get("LOG_LEVEL", "INFO").upper()
        if current_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            self.combo_level.setCurrentText(current_level)
            
        self.combo_level.currentTextChanged.connect(self.on_log_level_changed)
        top_layout.addWidget(self.combo_level)

        top_layout.addStretch()

        self.btn_clear = QPushButton(get("logviewer.clear_log"))
        self.btn_clear.setStyleSheet("background-color: #e63946; color: white; font-weight: bold;")
        self.btn_clear.clicked.connect(self.clear_log_file)
        top_layout.addWidget(self.btn_clear)

        layout.addLayout(top_layout)

        # --- TEXTAREA PER IL LOG --- #
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        
        font = QFont("Consolas" if os.name == "nt" else "Monospace", 10)
        self.text_area.setFont(font)
        self.text_area.setStyleSheet(
            "background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333;"
        )
        layout.addWidget(self.text_area)

        # --- TIMER PER AGGIORNAMENTO DINAMICO --- #
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.read_new_logs)
        self.timer.start()

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        self.load_full_log()

        i18n_bridge.status_changed.connect(self.update_ui)

    def format_log_line(self, line: str) -> str:
        """Converte una riga di log in HTML colorato in base al livello."""
        
        colors = {
            "ERROR": "#ff6b6b",
            "WARNING": "#feca57",
            "INFO": "#48dbfb",
            "DEBUG": "#a4b0be"
        }
        
        for level, color in colors.items( ):
            if f"[{level}]" in line:
                return f'<span style="color: {color};">{line}</span>'
        
        return f'<span style="color: #d4d4d4;">{line}</span>'

    def load_full_log(self):
        """Carica l'intero contenuto iniziale del file formattandolo a colori."""

        if os.path.exists(LOG_FILE_PATH):
            try:
                with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                    content = f.read().strip("\r\n")
                    if content:
                        lines = content.split("\n")
                        formatted_lines = [self.format_log_line(line) for line in lines]
                        self.text_area.setHtml("<br>".join(formatted_lines))
                        self.last_file_pos = f.tell()
                        QTimer.singleShot(10, self.scroll_to_bottom)
            except Exception as e:
                log.error(f"{get('log.logviewer.read_error')} {e}")

    def scroll_to_bottom(self):
        """Funzione di supporto per portare lo scroll in fondo."""

        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def read_new_logs(self):
        """Legge in modo incrementale i nuovi log e li appende formattati a colori."""

        if os.path.exists(LOG_FILE_PATH):
            try:
                with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                    f.seek(self.last_file_pos)
                    new_text = f.read()
                    if new_text:
                        self.last_file_pos = f.tell()
                        cleaned_text = new_text.strip("\r\n")
                        if cleaned_text:
                            lines = cleaned_text.split("\n")
                            formatted_lines = [self.format_log_line(line) for line in lines]
                            
                            cursor = self.text_area.textCursor()
                            cursor.movePosition(cursor.MoveOperation.End)
                            
                            for f_line in formatted_lines:
                                cursor.insertHtml("<br>" + f_line)
                            
                            self.text_area.verticalScrollBar().setValue(
                                self.text_area.verticalScrollBar().maximum()
                            )
            except Exception as e:
                pass

    def on_log_level_changed(self, new_level: str):
        """Cambia il livello di logging al volo sia in memoria che su config."""

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        if new_level in level_map:
            log.setLevel(level_map[new_level])
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
                new_level,
                config.get("THEME", "light"),
                config.get("LANGUAGE", get_system_locale())
            )

    def clear_log_file(self):
        """Chiede conferma e svuota il file di log."""

        reply = CustomMessageBox.ask_yes_no(self, "Conferma Pulizia", "Sei sicuro di voler cancellare l'intero contenuto del file di log?")

        if reply == "yes":
            try:
                with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
                    f.write("")
                self.text_area.clear()
                self.last_file_pos = 0
                log.info(get("log.logviewer.clear"))
            except Exception as e:
                CustomMessageBox.show_critical(self, "Errore", f"Impossibile svuotare il log: {e}")

    def update_ui(self):
        self.title_bar.title_label.setText(get("logviewer.title"))
        self.logging_level.setText(get("logviewer.logging_level"))
        self.btn_clear.setText(get("logviewer.clear_log"))

    def closeEvent(self, event):
        """Ferma il timer quando la finestra viene chiusa."""
        self.timer.stop()
        super().closeEvent(event)