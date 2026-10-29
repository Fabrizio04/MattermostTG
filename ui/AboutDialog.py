from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import  (
    QDialog, QVBoxLayout, QLabel, QPushButton, QWidget
)

from func.i18n import get
from func.window import initialize_window, exec_with_parent_dim

from settings import config
from version import __version__
from ui.CustomTitleBar import CustomTitleBar

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        initialize_window(self, 380, 280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title=get("about.title"))
        container_layout.addWidget(self.title_bar)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 12, 15, 15)

        # Titolo dell'App
        lbl_title = QLabel("🔔 Mattermost to Telegram Notifier")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        lbl_title.setFont(title_font)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        # Versione
        lbl_version = QLabel(f"{get('about.version')} {__version__} (Cross-Platform)")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_version)

        # Descrizione / Credits
        info_text = (
            f"{get('about.created')} Fabrizio\n"
            f"{get('about.license')}: Open Source (MIT)\n\n"
            f"{get('about.desc1')}\n"
            f"{get('about.desc2')}"
        )
        lbl_info = QLabel(info_text)
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)

        # Link GitHub
        link_color = "#48dbfb" if config.get("THEME", "light") == "dark" else "#0066cc"
        lbl_link = QLabel(f'<a href="https://github.com/Fabrizio04/MattermostTG" style="color: {link_color};">{get("about.url_text")}</a>')
        lbl_link.setOpenExternalLinks(True)
        lbl_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_link)

        # Pulsante di chiusura
        btn_close = QPushButton(get("about.btn_close"))
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        container_layout.addLayout(layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    @staticmethod
    def open_AboutDialog(parent):
        dlg = AboutDialog(parent=parent)
        exec_with_parent_dim(dlg, parent)