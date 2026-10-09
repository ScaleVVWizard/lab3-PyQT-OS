import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog


class Task3(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task3.ui", self)

        self.original = None
        self.current = None
        self.rotation = 0
        self.channel = "ALL"

        self.btnOpen.clicked.connect(self.on_open)
        self.btnRotLeft.clicked.connect(lambda: self._rotate(-90))
        self.btnRotRight.clicked.connect(lambda: self._rotate(90))
        self.btnReset.clicked.connect(self.on_reset)

        for rb in (self.rbAll, self.rbR, self.rbG, self.rbB):
            rb.toggled.connect(self.on_channel_changed)

        self.statusbar.showMessage("Откройте изображение")

    def _render(self):
        if self.original is None:
            self.lblImage.setText("Изображение не загружено")
            return

        img = self.original.toImage().convertToFormat(
            QtGui.QImage.Format.Format_ARGB32
        )

        if self.channel != "ALL":
            ch = {"R": 0, "G": 1, "B": 2}[self.channel]
            for y in range(img.height()):
                for x in range(img.width()):
                    px = img.pixelColor(x, y)
                    r, g, b = px.red(), px.green(), px.blue()
                    if ch == 0:
                        px.setRgb(r, 0, 0)
                    elif ch == 1:
                        px.setRgb(0, g, 0)
                    else:
                        px.setRgb(0, 0, b)
                    img.setPixelColor(x, y, px)

        pix = QtGui.QPixmap.fromImage(img)
        if self.rotation:
            transform = QtGui.QTransform().rotate(self.rotation)
            pix = pix.transformed(
                transform,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )

        self.current = pix
        self._show_pixmap()

    def _show_pixmap(self):
        if self.current is None:
            return
        scaled = self.current.scaled(
            self.lblImage.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.lblImage.setPixmap(scaled)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._show_pixmap()

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif);;Все файлы (*.*)"
        )
        if not path:
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден.")
            return

        pix = QtGui.QPixmap(path)
        if pix.isNull():
            QMessageBox.warning(self, "Ошибка",
                                "Не удалось загрузить изображение.\n"
                                "Возможно, формат не поддерживается.")
            return

        side = min(pix.width(), pix.height())
        x = (pix.width() - side) // 2
        y = (pix.height() - side) // 2
        pix = pix.copy(x, y, side, side)

        self.original = pix
        self.rotation = 0
        self.channel = "ALL"
        self.rbAll.setChecked(True)
        self.lblInfo.setText(
            f"Файл: {os.path.basename(path)}\n"
            f"Размер: {side}x{side} (обрезано до квадрата)"
        )
        self._render()
        self.statusbar.showMessage("Изображение загружено")

    def on_channel_changed(self):
        if self.rbR.isChecked():
            self.channel = "R"
        elif self.rbG.isChecked():
            self.channel = "G"
        elif self.rbB.isChecked():
            self.channel = "B"
        else:
            self.channel = "ALL"
        self._render()

    def _rotate(self, deg):
        if self.original is None:
            QMessageBox.information(self, "Нет изображения",
                                    "Сначала откройте изображение.")
            return
        self.rotation = (self.rotation + deg) % 360
        self._render()

    def on_reset(self):
        if self.original is None:
            return
        self.rotation = 0
        self.channel = "ALL"
        self.rbAll.setChecked(True)
        self._render()
        self.statusbar.showMessage("Сброшено")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task3()
    w.show()
    sys.exit(app.exec())