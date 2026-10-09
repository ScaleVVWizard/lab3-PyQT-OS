import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog


class Task4(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task4.ui", self)

        self.original = None
        self.current = None

        self.btnOpen.clicked.connect(self.on_open)
        self.btnReset.clicked.connect(self.on_reset)
        self.sliderAlpha.valueChanged.connect(self.on_alpha_changed)

        self.statusbar.showMessage("Откройте изображение")

    def _apply_alpha(self, value: int):
        if self.original is None:
            return
        img = self.original.toImage().convertToFormat(
            QtGui.QImage.Format.Format_ARGB32
        )
        for y in range(img.height()):
            for x in range(img.width()):
                c = img.pixelColor(x, y)
                a = c.alpha()
                new_a = (a * value) // 255 if a < 255 else value
                c.setAlpha(new_a)
                img.setPixelColor(x, y, c)
        self.current = QtGui.QPixmap.fromImage(img)
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
                                "Не удалось загрузить изображение.")
            return

        self.original = pix
        self.lblInfo.setText(
            f"Файл: {os.path.basename(path)}  ({pix.width()}x{pix.height()})"
        )
        self.on_alpha_changed(self.sliderAlpha.value())
        self.statusbar.showMessage("Изображение загружено")

    def on_alpha_changed(self, value: int):
        self.lblAlphaValue.setText(str(value))
        self._apply_alpha(value)

    def on_reset(self):
        self.sliderAlpha.setValue(255)
        self.statusbar.showMessage("Прозрачность сброшена")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task4()
    w.show()
    sys.exit(app.exec())