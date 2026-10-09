import sys
import os
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog


class Task2(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task2.ui", self)

        self.current_path = None
        self.dirty = False

        self.btnNew.clicked.connect(self.on_new)
        self.btnOpen.clicked.connect(self.on_open)
        self.btnSave.clicked.connect(self.on_save)
        self.btnSaveAs.clicked.connect(self.on_save_as)

        # отслеживаем изменения
        self.textEdit.textChanged.connect(self._on_text_changed)

        self._update_title()
        self.statusbar.showMessage("Готово")

    # ---------- helpers ----------
    def _update_title(self):
        name = os.path.basename(self.current_path) if self.current_path else "Новый файл"
        star = "*" if self.dirty else ""
        self.setWindowTitle(f"Task2 — {star}{name}")
        self.lblState.setText(("● " if self.dirty else "") + name)

    def _on_text_changed(self):
        if not self.dirty:
            self.dirty = True
            self._update_title()

    def _set_text_silent(self, text: str):
        """Установить текст без пометки dirty."""
        self.textEdit.blockSignals(True)
        self.textEdit.setPlainText(text)
        self.textEdit.blockSignals(False)
        self.dirty = False
        self._update_title()

    def _maybe_save(self) -> bool:
        if not self.dirty:
            return True
        r = QMessageBox.question(
            self, "Несохранённые изменения",
            "Есть несохранённые изменения. Сохранить?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        if r == QMessageBox.StandardButton.Cancel:
            return False
        if r == QMessageBox.StandardButton.Save:
            return self.on_save()
        return True

    # ---------- slots ----------
    def on_new(self):
        if not self._maybe_save():
            return
        self.current_path = None
        self._set_text_silent("")
        self.statusbar.showMessage("Создан новый файл")

    def on_open(self):
        if not self._maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "",
            "Текстовые файлы (*.txt *.md *.log *.py);;Все файлы (*.*)"
        )
        if not path:
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Ошибка", "Файл не существует.")
            return

        content = None
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="cp1251") as f:
                    content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось прочитать файл:\n{e}")
                return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось открыть файл:\n{e}")
            return

        self.current_path = path
        self._set_text_silent(content)
        self.statusbar.showMessage(f"Открыт: {path}")

    def on_save(self) -> bool:
        if self.current_path is None:
            return self.on_save_as()
        try:
            with open(self.current_path, "w", encoding="utf-8") as f:
                f.write(self.textEdit.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось сохранить файл:\n{e}")
            return False
        self.dirty = False
        self._update_title()
        self.statusbar.showMessage("Сохранено")
        return True

    def on_save_as(self) -> bool:
        default = self.current_path or "untitled.txt"
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", default,
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if not path:
            return False
        self.current_path = path
        return self.on_save()

    def closeEvent(self, e):
        if not self._maybe_save():
            e.ignore()
        else:
            e.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task2()
    w.show()
    sys.exit(app.exec())