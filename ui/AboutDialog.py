import os

from PyQt6.QtWidgets import  (
    QDialog, QVBoxLayout, QLabel, QPushButton, QWidget
)

from settings import config
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon
from func.utils import resource_path
from ui.DimmerOverlay import DimmerOverlay
from ui.CustomTitleBar import CustomTitleBar

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setWindowTitle("Informazioni su Mattermost Notifier")
        self.setFixedSize(380, 280)
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

        self.title_bar = CustomTitleBar(self, title="Informazioni su Mattermost Notifier")
        container_layout.addWidget(self.title_bar)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 12, 15, 15) # Left, Top, Right, Bottom

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
        link_color = "#48dbfb" if config.get("THEME", "light") == "dark" else "#0066cc"
        lbl_link = QLabel(f'<a href="https://github.com/Fabrizio04/MattermostTG" style="color: {link_color};">Visita il repository su GitHub</a>')
        lbl_link.setOpenExternalLinks(True)
        lbl_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_link)

        # Pulsante di chiusura
        btn_close = QPushButton("Chiudi")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        # self.setLayout(layout)

    @staticmethod
    def open_AboutDialog(parent):
        dlg = AboutDialog(parent=parent)
        AboutDialog._exec_with_parent_dim(dlg, parent)

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