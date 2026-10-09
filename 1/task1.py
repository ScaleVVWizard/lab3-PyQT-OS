import sys
import os
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog


class Task1(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task1.ui", self)

        self.current_data = None
        self.source_file = None

        self.btnLoad.clicked.connect(self.on_load)
        self.btnSave.clicked.connect(self.on_save)
        self.btnClear.clicked.connect(self.on_clear)

        self._set_fields("", "", "", "")
        self.log("Программа запущена. Загрузите txt-файл с целыми числами.")
        self.statusbar.showMessage("Готово")

    # ---------- helpers ----------
    def log(self, msg: str):
        self.txtLog.appendPlainText(msg)

    def _set_fields(self, mx, mn, avg, count):
        self.edMax.setText(str(mx))
        self.edMin.setText(str(mn))
        self.edAvg.setText(str(avg))
        self.edCount.setText(str(count))

    # ---------- slots ----------
    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите текстовый файл", "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if not path:
            self.txtLog.clear()
            self.log("Загрузка отменена.")
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Ошибка", "Файл не найден.")
            return
        if not path.lower().endswith(".txt"):
            QMessageBox.warning(self, "Ошибка",
                                "Разрешены только файлы формата .txt")
            return

        raw = None
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="cp1251") as f:
                    raw = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось прочитать файл:\n{e}")
                return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось открыть файл:\n{e}")
            return

      
        self.txtLog.clear()
        self._set_fields("", "", "", "")
        self.current_data = None
        self.source_file = None
       

        tokens = raw.split()
        if not tokens:
            QMessageBox.warning(self, "Пустой файл",
                                "Файл не содержит данных.")
            self.log("Файл пуст.")
            return

        numbers, bad = [], []
        for i, t in enumerate(tokens, 1):
            try:
                numbers.append(int(t))
            except ValueError:
                bad.append((i, t))

        if bad:
            preview = "\n".join(f"  токен №{i}: «{t}»" for i, t in bad[:10])
            more = "" if len(bad) <= 10 else f"\n… и ещё {len(bad)-10}"
            QMessageBox.warning(
                self, "Некорректные данные",
                f"Найдены не-целые значения:\n{preview}{more}\n\n"
                "Они будут проигнорированы."
            )
            self.log(f"Пропущено некорректных токенов: {len(bad)}")

        if not numbers:
            QMessageBox.critical(self, "Ошибка",
                                 "В файле нет ни одного целого числа.")
            self.log("Нет чисел для обработки.")
            return

        mx = max(numbers)
        mn = min(numbers)
        avg = sum(numbers) / len(numbers)
        cnt = len(numbers)

        self.current_data = {"max": mx, "min": mn, "avg": avg, "count": cnt}
        self.source_file = path

        self._set_fields(mx, mn, f"{avg:.6f}", cnt)
        self.log(f"Загружено: {os.path.basename(path)}")
        self.log(f"  max={mx}  min={mn}  avg={avg:.6f}  n={cnt}")
        self.statusbar.showMessage(f"Загружено чисел: {cnt}")

    def on_save(self):
        if self.current_data is None:
            QMessageBox.information(self, "Нет данных",
                                    "Сначала загрузите файл с числами.")
            return

        default_name = "stats.txt"
        if self.source_file:
            base = os.path.splitext(os.path.basename(self.source_file))[0]
            default_name = f"{base}_stats.txt"

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить статистику", default_name,
            "Текстовые файлы (*.txt)"
        )
        if not path:
            self.log("Сохранение отменено.")
            return

        if not path.lower().endswith(".txt"):
            path += ".txt"

        d = self.current_data
        text = (
            f"Максимальное значение: {d['max']}\n"
            f"Минимальное значение: {d['min']}\n"
            f"Среднее значение: {d['avg']:.6f}\n"
            f"Количество чисел: {d['count']}\n"
        )
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось сохранить файл:\n{e}")
            return

        self.log(f"Сохранено: {path}")
        QMessageBox.information(self, "Готово", "Статистика сохранена.")
        self.statusbar.showMessage("Файл сохранён")

    def on_clear(self):
        self.current_data = None
        self.source_file = None
        self._set_fields("", "", "", "")
        self.txtLog.clear()
        self.log("Данные очищены. Можно загрузить новый файл.")
        self.statusbar.showMessage("Очищено")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task1()
    w.show()
    sys.exit(app.exec())