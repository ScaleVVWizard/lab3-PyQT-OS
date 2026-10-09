import sys
import os
import random
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt6.QtGui import QColor, QPainter, QPixmap


class Task5(QtWidgets.QMainWindow):
    MIN_COLORS = 2
    MAX_COLORS = 12

    def __init__(self):
        super().__init__()
        uic.loadUi("task5.ui", self)

        self.flag_pixmap = None   # QPixmap флага
        self.colors = []          # список QColor

        self.btnGenerate.clicked.connect(self.on_generate)
        self.btnSave.clicked.connect(self.on_save)
        self.btnClear.clicked.connect(self.on_clear)

        self.statusbar.showMessage("Нажмите «Создать флаг…»")

    # ---------- helpers ----------
    def _build_flag(self, colors):
        """Строим QPixmap с горизонтальными полосами."""
        w, h = 600, 400
        pix = QPixmap(w, h)
        pix.fill(QColor(0, 0, 0, 0))  # прозрачный фон

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        n = len(colors)
        stripe_h = h / n
        for i, c in enumerate(colors):
            y = int(round(i * stripe_h))
            h_i = int(round((i + 1) * stripe_h)) - y
            painter.fillRect(0, y, w, h_i, c)
        painter.end()
        return pix

    def _show_flag(self):
        if self.flag_pixmap is None:
            return
        scaled = self.flag_pixmap.scaled(
            self.lblFlag.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.lblFlag.setPixmap(scaled)

    def _update_palette_label(self):
        if not self.colors:
            self.lblColors.setText("—")
            return
        parts = []
        for c in self.colors:
            parts.append(f"<span style='color:{c.name()};'>■</span>")
        parts.append(f"<span style='color:#ddd;'>({len(self.colors)} шт.)</span>")
        self.lblColors.setText(" ".join(parts))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._show_flag()

    # ---------- slots ----------
    def on_generate(self):
        n, ok = QInputDialog.getInt(
            self, "Количество цветов",
            f"Введите количество цветов ({self.MIN_COLORS}–{self.MAX_COLORS}):",
            value=3, min=self.MIN_COLORS, max=self.MAX_COLORS, step=1
        )
        if not ok:
            self.statusbar.showMessage("Генерация отменена")
            return

        # QInputDialog.getInt уже ограничивает min/max, но проверим на всякий случай
        if not (self.MIN_COLORS <= n <= self.MAX_COLORS):
            QMessageBox.warning(
                self, "Некорректное значение",
                f"Число должно быть в диапазоне "
                f"{self.MIN_COLORS}–{self.MAX_COLORS}."
            )
            return

        self.colors = [
            QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            for _ in range(n)
        ]

        self.flag_pixmap = self._build_flag(self.colors)
        self._show_flag()
        self._update_palette_label()
        self.lblInfo.setText(f"Цветов: {n}")
        self.statusbar.showMessage(f"Флаг создан: {n} цветов")

    def on_save(self):
        if self.flag_pixmap is None:
            QMessageBox.information(self, "Нет флага",
                                    "Сначала создайте флаг.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить флаг", "flag.png",
            "PNG-изображение (*.png)"
        )
        if not path:
            self.statusbar.showMessage("Сохранение отменено")
            return
        if not path.lower().endswith(".png"):
            path += ".png"

        if not self.flag_pixmap.save(path, "PNG"):
            QMessageBox.critical(self, "Ошибка",
                                 "Не удалось сохранить изображение.")
            return

        self.statusbar.showMessage(f"Сохранено: {os.path.basename(path)}")
        QMessageBox.information(self, "Готово", "Флаг сохранён.")

    def on_clear(self):
        self.flag_pixmap = None
        self.colors = []
        self.lblFlag.setPixmap(QPixmap())     # пустая картинка
        self.lblFlag.setText("Флаг не создан")
        self.lblInfo.setText("Флаг не создан")
        self.lblColors.setText("—")
        self.statusbar.showMessage("Очищено")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task5()
    w.show()
    sys.exit(app.exec())