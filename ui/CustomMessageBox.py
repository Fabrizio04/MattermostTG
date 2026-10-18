from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QApplication, QGraphicsColorizeEffect, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from ui.CustomTitleBar import CustomTitleBar
from PyQt6.QtGui import QColor
from ui.DimmerOverlay import DimmerOverlay

from settings import config

class CustomMessageBox(QDialog):
    def __init__(self, title, message, icon_type="info", buttons=None, parent=None):
        super().__init__(parent)

        QApplication.beep()
        
        # Window Frameless con trasparenza per gli angoli
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(400)
        
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

        self.selected_button = None # Terrà traccia della risposta

        # Layout Radice
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # MainContainer interno (sfondo e bordi arrotondati)
        container = QWidget(self)
        container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 1. Title bar custom
        self.title_bar = CustomTitleBar(self, title=title)
        # self.title_bar.setFixedHeight(35)
        container_layout.addWidget(self.title_bar)

        # 2. Contenuto (Icona + Messaggio affiancati)
        body_widget = QWidget()
        body_widget.setObjectName("MessageBoxBody")
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(20, 15, 20, 20)
        body_layout.setSpacing(15)

        # Icona nitida
        icon_label = QLabel()
        style = self.style()
        if icon_type == "warning":
            standard_icon = style.StandardPixmap.SP_MessageBoxWarning
        elif icon_type == "critical":
            standard_icon = style.StandardPixmap.SP_MessageBoxCritical
        elif icon_type == "question":
            standard_icon = style.StandardPixmap.SP_MessageBoxQuestion
        else:
            standard_icon = style.StandardPixmap.SP_MessageBoxInformation

        icon = style.standardIcon(standard_icon)
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        body_layout.addWidget(icon_label)

        # Testo del messaggio
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        body_layout.addWidget(msg_label, stretch=1)

        container_layout.addWidget(body_widget)

        # 3. Layout Pulsanti Dinamici
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 0, 20, 20)
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        if not buttons:
            buttons = [("OK", "accept")]

        for text, result_key in buttons:
            btn = QPushButton(text)
            btn.setFixedWidth(95)
            # Creiamo una funzione di chiusura che memorizza quale bottone è stato premuto
            btn.clicked.connect(lambda checked, r=result_key: self.on_button_clicked(r))
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        container_layout.addLayout(btn_layout)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def on_button_clicked(self, result_key):
        self.selected_button = result_key
        self.accept()

    def accept(self):
        if getattr(self, '_is_closing', False):
            return
        self._is_closing = True
        # Usiamo QDialog anziché super() per evitare l'errore di scope nella lambda
        self.start_fade_out(lambda: QDialog.accept(self))

    def reject(self):
        if getattr(self, '_is_closing', False):
            return
        self._is_closing = True
        self.start_fade_out(lambda: QDialog.reject(self))

    def start_fade_out(self, callback):
        if hasattr(self, 'fade_out_anim') and self.fade_out_anim.state() == QPropertyAnimation.State.Running:
            return

        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(150)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Sostituiamo la connessione pulita con una lambda che assicura lo sblocco di exec()
        self.fade_out_anim.finished.connect(callback)
        self.fade_out_anim.start()

    # --- Metodi di comodo statici ---
    @staticmethod
    def show_info(parent, title, message):
        dlg = CustomMessageBox(title, message, icon_type="info", buttons=[("OK", "ok")], parent=parent)
        CustomMessageBox._exec_with_parent_dim(dlg, parent)

    @staticmethod
    def show_warning(parent, title, message):
        dlg = CustomMessageBox(title, message, icon_type="warning", buttons=[("OK", "ok")], parent=parent)
        CustomMessageBox._exec_with_parent_dim(dlg, parent)

    @staticmethod
    def show_warning_on_start(title, message):
        dlg = CustomMessageBox(title, message, icon_type="warning", buttons=[("OK", "ok")], parent=None)
        dlg.exec()

    @staticmethod
    def show_critical(parent, title, message):
        dlg = CustomMessageBox(title, message, icon_type="critical", buttons=[("OK", "ok")], parent=parent)
        CustomMessageBox._exec_with_parent_dim(dlg, parent)

    @staticmethod
    def ask_save_changes(parent, title, message):
        """Mostra il dialogo con 3 opzioni: Salva, Scarta, Annulla"""
        buttons = [
            ("Salva", "save"),
            ("Scarta", "discard"),
            ("Annulla", "cancel")
        ]
        dlg = CustomMessageBox(title, message, icon_type="question", buttons=buttons, parent=parent)
        CustomMessageBox._exec_with_parent_dim(dlg, parent)
        return dlg.selected_button

    @staticmethod
    def ask_yes_no(parent, title, message):
        """Mostra un dialogo di conferma con 2 pulsanti: Sì e No (o Yes e No)"""
        buttons = [
            ("Sì", "yes"),
            ("No", "no")
        ]
        dlg = CustomMessageBox(title, message, icon_type="question", buttons=buttons, parent=parent)
        #dlg.exec()
        CustomMessageBox._exec_with_parent_dim(dlg, parent)
        return dlg.selected_button

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
        