import os

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPoint

from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, 
    QPushButton, QWidget
)

from func.utils import resource_path

class CustomTitleBar(QWidget):
    """Barra del titolo personalizzata, tematizzabile e cross-platform."""

    def __init__(self, parent=None, title="None"):
        super().__init__(parent)
        self.parent = parent
        self.start_pos = QPoint()

        # Layout orizzontale per la barra
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 5, 5)
        layout.setSpacing(8)

        # Icona
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(resource_path(os.path.join("img", "icon_active.png"))).pixmap(16, 16))
        layout.addWidget(self.icon_label)

        # Titolo della finestra
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Pulsante Riduci a Icona
        # self.btn_minimize = QPushButton("—")
        # self.btn_minimize.setFixedSize(28, 24)
        # self.btn_minimize.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # self.btn_minimize.clicked.connect(self.parent.showMinimized)
        # layout.addWidget(self.btn_minimize)

        # Pulsante Chiudi
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_close.clicked.connect(self.parent.close)
        layout.addWidget(self.btn_close)

        self.setObjectName("CustomTitleBar")
        self.btn_close.setObjectName("TitleBarCloseBtn")

    # --- Gestione del trascinamento finestra --- #
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.start_pos:
            self.parent.move(event.globalPosition().toPoint() - self.start_pos)
            event.accept()