import sys
import os
import math
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import QPointF, Qt


MAX_STRING_LEN = 1_500_000
MAX_STEP = 15


class LSystem:
    def __init__(self, title, angles, axiom, rules):
        self.title = title
        self.angles = angles
        self.axiom = axiom
        self.rules = rules
        self.angle_deg = 360.0 / angles
        self.cache = {0: axiom}

    def get(self, step):
        if step in self.cache:
            return self.cache[step]
        prev = self.get(step - 1)
        out = []
        total = 0
        for ch in prev:
            repl = self.rules.get(ch, ch)
            total += len(repl)
            if total > MAX_STRING_LEN:
                raise RuntimeError(
                    f"Строка шага {step} превысит {MAX_STRING_LEN} символов"
                )
            out.append(repl)
        result = "".join(out)
        self.cache[step] = result
        return result


def parse_lsystem(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) < 3:
        raise ValueError("Файл слишком короткий: нужно минимум 3 строки")

    title = lines[0].strip()
    if not title:
        raise ValueError("Первая строка (название) пустая")

    try:
        angles = int(lines[1].strip())
    except ValueError:
        raise ValueError("Вторая строка должна быть целым числом (число углов)")
    if angles < 1 or angles > 360:
        raise ValueError("Число углов должно быть в диапазоне 1..360")

    axiom = lines[2].strip()
    if not axiom:
        raise ValueError("Третья строка (аксиома) пустая")

    rules = {}
    for i, ln in enumerate(lines[3:], start=4):
        s = ln.strip()
        if not s:
            continue
        if "=" not in s:
            raise ValueError(f"Строка {i}: нет знака '=' в правиле: {s}")
        left, right = s.split("=", 1)
        left = left.strip()
        right = right.strip()
        if len(left) != 1:
            raise ValueError(f"Строка {i}: левая часть правила должна быть одним символом")
        if not right:
            raise ValueError(f"Строка {i}: правая часть правила пустая")
        rules[left] = right

    if not rules:
        raise ValueError("Не найдено ни одного правила")

    return LSystem(title, angles, axiom, rules)


def string_to_segments(s, angle_deg, step_len):
    segments = []
    x, y = 0.0, 0.0
    direction = -math.pi / 2
    stack = []
    angle_rad = math.radians(angle_deg)

    min_x = max_x = x
    min_y = max_y = y

    for ch in s:
        if ch in ("F", "A", "B"):
            nx = x + step_len * math.cos(direction)
            ny = y + step_len * math.sin(direction)
            segments.append((x, y, nx, ny))
            x, y = nx, ny
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
        elif ch == "f":
            x = x + step_len * math.cos(direction)
            y = y + step_len * math.sin(direction)
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
        elif ch == "+":
            direction += angle_rad
        elif ch == "-":
            direction -= angle_rad
        elif ch == "[":
            stack.append((x, y, direction))
        elif ch == "]":
            if stack:
                x, y, direction = stack.pop()
        elif ch == "|":
            direction += math.pi
        else:
            continue

    if not segments:
        return segments, 0, 0, 0, 0
    return segments, min_x, min_y, max_x, max_y


class Task8(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task8.ui", self)

        self.lsystem = None
        self.current_path = None
        self.max_step = 0
        self.lines = []
        self.bounds = None
        self._skip_slider_signal = False

        self.btnOpen.clicked.connect(self.on_open)
        self.btnReload.clicked.connect(self.on_reload)
        self.btnFit.clicked.connect(self.render_current)
        self.btnSavePng.clicked.connect(self.on_save_png)
        self.sliderStep.valueChanged.connect(self.on_step_changed)

        self.lblCanvas.setText("Откройте файл с определением L-системы")
        self.statusbar.showMessage("Готово")

        QtCore.QTimer.singleShot(200, self.on_open_first_launch)

    def on_open_first_launch(self):
        self.on_open()

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть определение L-системы", "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if not path:
            self.statusbar.showMessage("Открытие отменено")
            return
        self.load_file(path)

    def on_reload(self):
        if not self.current_path:
            QMessageBox.information(self, "Нет файла",
                                    "Сначала откройте файл.")
            return
        self.load_file(self.current_path)

    def load_file(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден.")
            return
        try:
            self.lsystem = parse_lsystem(path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка парсинга",
                                 f"Не удалось разобрать файл:\n{e}")
            self.statusbar.showMessage("Ошибка парсинга")
            return

        self.current_path = path
        self.lblTitle.setText(f"Файл: {self.lsystem.title}")
        self.lblAxiom.setText(f"Аксиома: {self.lsystem.axiom}")
        self.lblAngle.setText(
            f"Угол: {self.lsystem.angle_deg:.2f}° (360/{self.lsystem.angles})"
        )
        self.lblRules.setText(f"Правил: {len(self.lsystem.rules)}")

        self._compute_max_step()
        self._skip_slider_signal = True
        self.sliderStep.setMinimum(0)
        self.sliderStep.setMaximum(self.max_step)
        self.sliderStep.setValue(1 if self.max_step >= 1 else 0)
        self._skip_slider_signal = False

        self.render_current()
        self.statusbar.showMessage(f"Загружено: {self.lsystem.title}")

    def _compute_max_step(self):
        limit = MAX_STEP
        for step in range(1, MAX_STEP + 1):
            try:
                s = self.lsystem.get(step)
                if len(s) > MAX_STRING_LEN:
                    limit = step - 1
                    break
            except RuntimeError:
                limit = step - 1
                break
        self.max_step = max(1, limit)

    def on_step_changed(self, value):
        if self._skip_slider_signal:
            return
        self.lblStepValue.setText(f"{value} / {self.max_step}")
        self.render_current()

    def render_current(self):
        if self.lsystem is None:
            return
        step = self.sliderStep.value()
        try:
            s = self.lsystem.get(step)
        except RuntimeError as e:
            QMessageBox.warning(self, "Слишком длинная строка", str(e))
            self.sliderStep.setValue(step - 1)
            return

        self.lblLength.setText(f"Длина строки: {len(s)}")
        self.lblStepValue.setText(f"{step} / {self.max_step}")

        segments, min_x, min_y, max_x, max_y = string_to_segments(
            s, self.lsystem.angle_deg, 1.0
        )
        self.lines = segments
        self.bounds = (min_x, min_y, max_x, max_y)
        self._draw()

    def _draw(self):
        w = max(self.lblCanvas.width(), 100)
        h = max(self.lblCanvas.height(), 100)

        pix = QPixmap(w, h)
        pix.fill(QColor(250, 250, 250))

        if not self.lines or self.bounds is None:
            self.lblCanvas.setPixmap(pix)
            return

        min_x, min_y, max_x, max_y = self.bounds
        span_x = max_x - min_x
        span_y = max_y - min_y
        if span_x <= 0: span_x = 1.0
        if span_y <= 0: span_y = 1.0

        margin = 20
        scale_x = (w - 2 * margin) / span_x
        scale_y = (h - 2 * margin) / span_y
        scale = min(scale_x, scale_y)

        offset_x = margin + (-min_x) * scale
        offset_y = margin + (-min_y) * scale

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(QColor(20, 20, 20))
        pen.setWidthF(1.0)
        painter.setPen(pen)

        for (x1, y1, x2, y2) in self.lines:
            painter.drawLine(
                QPointF(x1 * scale + offset_x, y1 * scale + offset_y),
                QPointF(x2 * scale + offset_x, y2 * scale + offset_y)
            )
        painter.end()

        self.lblCanvas.setPixmap(pix)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._draw()

    def on_save_png(self):
        if self.lsystem is None or self.lblCanvas.pixmap() is None:
            QMessageBox.information(self, "Нет изображения",
                                    "Сначала постройте L-систему.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить PNG", "lsystem.png",
            "PNG-изображение (*.png)"
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        if not self.lblCanvas.pixmap().save(path, "PNG"):
            QMessageBox.critical(self, "Ошибка",
                                 "Не удалось сохранить PNG.")
            return
        QMessageBox.information(self, "Готово", "Изображение сохранено.")
        self.statusbar.showMessage(f"Сохранено: {os.path.basename(path)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task8()
    w.show()
    sys.exit(app.exec())