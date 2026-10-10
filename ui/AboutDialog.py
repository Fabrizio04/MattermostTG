from PyQt6.QtWidgets import  (
    QDialog, QVBoxLayout, QLabel, QPushButton
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni su Mattermost Notifier")
        self.setFixedSize(380, 260)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        # Titolo dell'App
        lbl_title = QLabel("🔔 Mattermost to Telegram Notifier")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        # Versione
        lbl_version = QLabel("Versione 1.1.0 (Cross-Platform)")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_version)

        # Descrizione / Credits
        info_text = (
            "Creato con cura da Fabrizio\n"
            "Licenza: Open Source (MIT)\n\n"
            "Un'applicazione tray leggera, sicura ed elegante\n"
            "per inoltrare notifiche in tempo reale."
        )
        lbl_info = QLabel(info_text)
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)

        # Link GitHub cliccabile
        lbl_link = QLabel('<a href="https://github.com/Fabrizio04/MattermostTG">Visita il repository su GitHub</a>')
        lbl_link.setOpenExternalLinks(True)
        lbl_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_link)

        # Pulsante di chiusura
        btn_close = QPushButton("Chiudi")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)