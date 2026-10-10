from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtWidgets import QCheckBox

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(50, 24)
        
        # Posizione iniziale basata sullo stato
        self._circle_position = 27.0 if self.isChecked() else 3.0
        
        # Colleghiamo il segnale del cambio stato
        self.stateChanged.connect(self._trigger_animation)

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circlePosition = pyqtProperty(float, get_circle_position, set_circle_position)

    def setChecked(self, checked):
        super().setChecked(checked)
        self._circle_position = 27.0 if checked else 3.0
        self.update()

    def _trigger_animation(self, state):
        checked = (state == 2)
        target_pos = 27.0 if checked else 3.0
        
        # Se siamo già nella posizione giusta, evitiamo animazioni superflue
        if self._circle_position == target_pos:
            return

        self.animation = QPropertyAnimation(self, b"circlePosition")
        self.animation.setDuration(150)
        
        start_val = self._circle_position
        end_val = target_pos
        
        self.animation.setStartValue(start_val)
        self.animation.setEndValue(end_val)
        self.animation.start()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        bg_color = QColor(0, 180, 216) if self.isChecked() else QColor(200, 200, 200)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(QRectF(0, 0, 50, 24), 12, 12)

        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QRectF(self._circle_position, 3.0, 18.0, 18.0))
        
        painter.end()