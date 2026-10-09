import sys
import os
from PyQt6 import QtWidgets, QtCore, QtMultimedia, uic
from PyQt6.QtWidgets import (
    QMessageBox, QFileDialog, QInputDialog, QListWidgetItem
)


NOTES = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

EXTS = [".wav", ".aiff", ".aif", ".mp3", ".ogg", ".flac"]

PREFIXES = ["Piano.mf.", "Piano.pp.", "Piano.ff.", "Piano.", ""]

MELODIES = {
    "up":    ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"],
    "down":  ["C5", "B4", "A4", "G4", "F4", "E4", "D4", "C4"],
    "chord": ["C4", "E4", "G4", "C5"],
    "chord_down": ["C5", "G4", "E4", "C4"],
}


class Task7(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task7.ui", self)

        base = os.path.dirname(os.path.abspath(__file__))
        self.sounds_dir = os.path.join(base, "sounds")

        self.player = QtMultimedia.QSoundEffect(self)
        self.player.setVolume(0.9)

        self.recording = False
        self.recorded = []

        self.queue = []
        self.queue_index = 0
        self.is_playing_queue = False

        self.queue_timer = QtCore.QTimer(self)
        self.queue_timer.setSingleShot(True)
        self.queue_timer.timeout.connect(self._play_next_in_queue)

        self._buttons = {
            "C4": self.btnC4, "D4": self.btnD4, "E4": self.btnE4, "F4": self.btnF4,
            "G4": self.btnG4, "A4": self.btnA4, "B4": self.btnB4, "C5": self.btnC5,
        }

        for name, btn in self._buttons.items():
            btn.clicked.connect(lambda _=False, n=name: self.play_note(n))

        self.btnPickFolder.clicked.connect(self.on_pick_folder)
        self.btnCheckFiles.clicked.connect(self.on_check_files)

        self.btnMel1.clicked.connect(lambda: self.start_melody(MELODIES["up"]))
        self.btnMel2.clicked.connect(lambda: self.start_melody(MELODIES["down"]))
        self.btnMel3.clicked.connect(lambda: self.start_melody(MELODIES["chord"]))
        if hasattr(self, "btnMel4"):
            self.btnMel4.clicked.connect(lambda: self.start_melody(MELODIES["chord_down"]))

        if hasattr(self, "sliderTempo"):
            self.sliderTempo.valueChanged.connect(self.on_tempo_changed)
            self.lblTempoValue.setText(f"{self.sliderTempo.value()} мс")

        if hasattr(self, "btnStopPlayback"):
            self.btnStopPlayback.clicked.connect(self.stop_playback)

        self.btnRecord.clicked.connect(self.on_record)
        self.btnStopRecord.clicked.connect(self.on_stop_record)
        self.btnPlay.clicked.connect(self.on_play_recorded)
        self.btnClearList.clicked.connect(self.on_clear_list)
        self.btnRemoveSelected.clicked.connect(self.on_remove_selected)

        self.btnAddNote.clicked.connect(self.on_add_note)
        self.btnRemoveNote.clicked.connect(self.on_remove_selected)
        self.btnMoveUp.clicked.connect(lambda: self.move_selected(-1))
        self.btnMoveDown.clicked.connect(lambda: self.move_selected(1))
        self.btnPlayOne.clicked.connect(self.on_play_selected)

        self.lblFolder.setText(f"Папка: {self.sounds_dir}")
        self._check_files_silent()
        self.statusbar.showMessage("Готово")

    # ---------- поиск файлов ----------
    def _candidates(self, note):
        names = []
        for prefix in PREFIXES:
            for ext in EXTS:
                names.append(f"{prefix}{note}{ext}")
        return names

    def _note_path(self, note):
        if not os.path.isdir(self.sounds_dir):
            return None
        existing = set(os.listdir(self.sounds_dir))
        for name in self._candidates(note):
            if name in existing:
                return os.path.join(self.sounds_dir, name)
        return None

    def _check_files_silent(self):
        for note, btn in self._buttons.items():
            path = self._note_path(note)
            exists = path is not None
            btn.setEnabled(exists)
            if exists:
                btn.setToolTip(f"Проиграть {note}\n{path}")
            else:
                btn.setToolTip(f"Нет файла для {note} в {self.sounds_dir}")

    # ---------- воспроизведение одной ноты ----------
    def _play_sound(self, note):
        path = self._note_path(note)
        if path is None:
            return False
        self.player.stop()
        self.player.setSource(QtCore.QUrl.fromLocalFile(path))
        self.player.play()
        return True

    def play_note(self, note):
        if self._note_path(note) is None:
            QMessageBox.warning(self, "Файл не найден",
                                f"Не найден файл для ноты {note}.\n"
                                f"Папка: {self.sounds_dir}")
            self.statusbar.showMessage(f"Нет файла для {note}")
            return
        self.stop_playback()
        self._play_sound(note)
        self._mark_record(note)
        self.statusbar.showMessage(f"Играет: {note}")

    # ---------- очередь мелодии ----------
    def start_melody(self, notes):
        for note in notes:
            if self._note_path(note) is None:
                QMessageBox.warning(self, "Файл не найден",
                                    f"Не найден файл для ноты {note}.")
                return
        self.stop_playback()
        self.queue = list(notes)
        self.queue_index = 0
        self.is_playing_queue = True
        self.statusbar.showMessage(f"Мелодия: {len(notes)} нот, "
                                   f"темп {self._tempo()} мс")
        self._play_next_in_queue()

    def _play_next_in_queue(self):
        if not self.is_playing_queue:
            return
        if self.queue_index >= len(self.queue):
            self.is_playing_queue = False
            self.statusbar.showMessage("Мелодия завершена")
            return
        note = self.queue[self.queue_index]
        self.queue_index += 1
        self._play_sound(note)
        self._mark_record(note)
        self.statusbar.showMessage(
            f"Нота {self.queue_index}/{len(self.queue)}: {note}"
        )
        self.queue_timer.start(self._tempo())

    def _tempo(self):
        if hasattr(self, "sliderTempo"):
            return self.sliderTempo.value()
        return 700

    def stop_playback(self):
        self.queue_timer.stop()
        self.is_playing_queue = False
        self.queue = []
        self.queue_index = 0
        self.player.stop()

    def on_tempo_changed(self, value):
        self.lblTempoValue.setText(f"{value} мс")
        if self.is_playing_queue:
            self.queue_timer.start(value)

    # ---------- папка и проверка ----------
    def on_pick_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку со звуками", self.sounds_dir
        )
        if not path:
            return
        self.sounds_dir = path
        self.lblFolder.setText(f"Папка: {self.sounds_dir}")
        self._check_files_silent()
        self.statusbar.showMessage("Папка обновлена")

    def on_check_files(self):
        missing = [n for n in NOTES if self._note_path(n) is None]
        if not missing:
            lines = [f"{n}: {os.path.basename(self._note_path(n))}" for n in NOTES]
            QMessageBox.information(self, "Все файлы на месте",
                                    "Найдены все ноты:\n\n" + "\n".join(lines))
        else:
            QMessageBox.warning(self, "Не хватает файлов",
                                "Отсутствуют ноты:\n" + "\n".join(missing) +
                                f"\n\nПапка: {self.sounds_dir}")
        self._check_files_silent()

    # ---------- запись ----------
    def _mark_record(self, note):
        if self.recording:
            self.recorded.append(note)
            self.listNotes.addItem(QListWidgetItem(note))
            self.listNotes.scrollToBottom()

    def on_record(self):
        self.recording = True
        self.recorded = []
        self.listNotes.clear()
        self.lblRecordState.setText("● Запись…")
        self.statusbar.showMessage("Запись начата")

    def on_stop_record(self):
        if not self.recording:
            self.statusbar.showMessage("Запись и не шла")
            return
        self.recording = False
        self.lblRecordState.setText(f"Записано нот: {len(self.recorded)}")
        self.statusbar.showMessage("Запись остановлена")

    # ---------- список ----------
    def on_play_recorded(self):
        notes = [self.listNotes.item(i).text() for i in range(self.listNotes.count())]
        if not notes:
            QMessageBox.information(self, "Пусто",
                                    "Список пуст. Запишите или добавьте ноты.")
            return
        self.start_melody(notes)

    def on_clear_list(self):
        if self.listNotes.count() == 0:
            return
        r = QMessageBox.question(self, "Очистить список",
                                 "Удалить все ноты из списка?")
        if r != QMessageBox.StandardButton.Yes:
            return
        self.listNotes.clear()
        self.recorded = []
        self.statusbar.showMessage("Список очищен")

    def on_remove_selected(self):
        row = self.listNotes.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ничего не выбрано",
                                    "Выберите ноту в списке.")
            return
        self.listNotes.takeItem(row)
        self.statusbar.showMessage("Удалено")

    def on_add_note(self):
        note, ok = QInputDialog.getItem(
            self, "Добавить ноту", "Выберите ноту:",
            NOTES, 0, False
        )
        if not ok:
            return
        self.listNotes.addItem(QListWidgetItem(note))
        self.listNotes.scrollToBottom()
        self.statusbar.showMessage(f"Добавлено: {note}")

    def move_selected(self, direction):
        row = self.listNotes.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ничего не выбрано",
                                    "Выберите ноту в списке.")
            return
        new_row = row + direction
        if new_row < 0 or new_row >= self.listNotes.count():
            return
        item = self.listNotes.takeItem(row)
        self.listNotes.insertItem(new_row, item)
        self.listNotes.setCurrentRow(new_row)

    def on_play_selected(self):
        item = self.listNotes.currentItem()
        if item is None:
            QMessageBox.information(self, "Ничего не выбрано",
                                    "Выберите ноту в списке.")
            return
        self.play_note(item.text())

    def closeEvent(self, e):
        self.stop_playback()
        e.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Task7()
    w.show()
    sys.exit(app.exec())