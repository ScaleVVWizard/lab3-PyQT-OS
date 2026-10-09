import sys
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from PyQt6.QtWidgets import QMessageBox, QColorDialog
from PyQt6.QtGui import QColor, QPainter, QPixmap, QPen, QBrush
from PyQt6.QtCore import QRectF, Qt


class Task6(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task6.ui", self)

        self.color = QColor(255, 212, 0)
        self.scale = 100

        self.btnColor.clicked.connect(self.on_pick_color)
        self.btnReset.clicked.connect(self.on_reset)
        self.sliderScale.valueChanged.connect(self.on_scale_changed)

        self.sliderScale.setTracking(True)
        self.lblScaleValue.setText(f"{self.sliderScale.value()}%")
        self._update_color_preview()
        self._render()
        self.statusbar.showMessage("Готово")

    def _update_color_preview(self):
        self.lblColorPreview.setStyleSheet(
            f"QLabel {{ background:{self.color.name()}; border:1px solid #888; }}"
        )

    def _render(self):
        side = min(self.lblCanvas.width(), self.lblCanvas.height())
        side = max(side, 50)

        pix = QPixmap(side, side)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        ratio = 0.40 * self.scale / 100.0
        radius = side * ratio
        cx, cy = side / 2, side / 2
        face_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        face_color = self.color
        outline = QColor(0, 0, 0) if face_color.lightness() > 128 else QColor(255, 255, 255)

        painter.setBrush(QBrush(face_color))
        pen = QPen(outline)
        pen.setWidthF(max(1.0, radius * 0.06))
        painter.setPen(pen)
        painter.drawEllipse(face_rect)

        eye_r = radius * 0.14
        eye_dx = radius * 0.36
        eye_dy = radius * 0.28
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(outline))
        painter.drawEllipse(QRectF(cx - eye_dx - eye_r, cy - eye_dy - eye_r,
                                   eye_r * 2, eye_r * 2))
        painter.drawEllipse(QRectF(cx + eye_dx - eye_r, cy - eye_dy - eye_r,
                                   eye_r * 2, eye_r * 2))

        mouth_rect = QRectF(
            cx - radius * 0.55, cy - radius * 0.10,
            radius * 1.10, radius * 0.85
        )
        pen = QPen(outline)
        pen.setWidthF(max(1.0, radius * 0.08))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(mouth_rect, 200 * 16, 140 * 16)

        painter.end()
        self.lblCanvas.setPixmap(pix)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._render()

    def on_pick_color(self):
        c = QColorDialog.getColor(self.color, self, "Выберите цвет смайлика")
        if not c.isValid():
            self.statusbar.showMessage("Выбор цвета отменён")
            return
        c.setAlpha(255)
        self.color = c
        self._update_color_preview()
        self._render()
        self.statusbar.showMessage(f"Цвет: {c.name()}")

    def on_scale_changed(self, value: int):
        self.scale = value
        self.lblScaleValue.setText(f"{value}%")
        self._render()

    def on_reset(self):
        self.color = QColor(255, 212, 0)
        self.sliderScale.setValue(100)
        self._update_color_preview()
        self._render()
        self.statusbar.showMessage("Сброшено")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task6()
    w.show()
    sys.exit(app.exec())