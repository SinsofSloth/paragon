import logging
import traceback

from PySide2 import QtGui
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QInputDialog, QMessageBox

from paragon.core.dialogue.scanner import ScannerError
from paragon.ui.controllers.error_dialog import ErrorDialog
from paragon.ui.views.ui_dialogue_editor import Ui_DialogueEditor


class DialogueEditor(Ui_DialogueEditor):
    def __init__(self, data, service, path, localized):
        super().__init__()
        self.data = data
        self.service = service
        self.path = path
        self.localized = localized
        self.message = None
        self.error_dialog = None

        self.setWindowTitle("Paragon - " + path)

        self.data.open_text_data(path, localized)
        keys = self.data.enumerate_messages(path, localized)
        for key in keys:
            self.keys_box.addItem(key)
        self.keys_box.setCurrentIndex(-1)

        backgrounds = self.service.backgrounds()
        self.player.set_backgrounds(backgrounds)
        windows = self.service.windows()
        self.player.set_windows(windows)
        self.player.set_service(self.service)

        self.player.redraw()
        self.refresh_buttons()

        self.keys_box.currentIndexChanged.connect(self._on_selection)
        self.preview_button.clicked.connect(self._on_save_and_preview)
        self.new_button.clicked.connect(self._on_new)
        self.delete_button.clicked.connect(self._on_delete)
        self.rename_button.clicked.connect(self._on_rename)

    def refresh_buttons(self):
        has_selection = self.keys_box.currentIndex() != -1
        self.preview_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.rename_button.setEnabled(has_selection)

    def _select_line(self, line):
        doc = self.editor.document()
        block = doc.findBlockByLineNumber(line)
        if block:
            cursor = QTextCursor(block)
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            self.editor.setTextCursor(cursor)

    def _on_selection(self):
        if self.keys_box.currentIndex() != -1:
            key = self.keys_box.currentText()
            value = self.data.message(self.path, self.localized, key)
            pretty = self.service.game_to_pretty(value)
            self.editor.setPlainText(pretty)
        else:
            self.editor.setPlainText("")
        self._preview()
        self.refresh_buttons()

    def _on_save_and_preview(self):
        if self.keys_box.currentIndex() != -1:
            if self._preview():
                self._save()

    def _preview(self):
        try:
            text = self.editor.toPlainText()
            snapshots = self.service.interpret(text)
            self.player.set_snapshots(snapshots)
            return True
        except ScannerError as e:
            self.error_dialog = ErrorDialog(str(e))
            self.error_dialog.show()
            self._select_line(e.line - 1)
        except Exception as e:
            logging.exception("Previewing failed.")
            trace = traceback.format_exception(type(e), e, e.__traceback__)
            self.error_dialog = ErrorDialog("".join(trace))
            self.error_dialog.show()
        return False

    def _save(self):
        try:
            text = self.editor.toPlainText()
            game_text = self.service.pretty_to_game(text)
            self.data.set_message(
                self.path, self.localized, self.keys_box.currentText(), game_text
            )
        except ScannerError as e:
            self.error_dialog = ErrorDialog(str(e))
            self.error_dialog.show()
            self._select_line(e.line - 1)
        except Exception as e:
            logging.exception("Previewing failed.")
            trace = traceback.format_exception(type(e), e, e.__traceback__)
            self.error_dialog = ErrorDialog("".join(trace))
            self.error_dialog.show()

    def _on_new(self):
        # TODO: Validate naming scheme?
        choice, ok = QInputDialog.getText(self, "Enter Key", "Key")
        if ok:
            self.data.set_message(
                self.path,
                self.localized,
                choice,
                "This is a placeholder message.\\nSee the guide for info on formatting.",
            )
            self.keys_box.addItem(choice)
            self.keys_box.setCurrentIndex(self.keys_box.count() - 1)

    def _on_delete(self):
        if self.keys_box.currentIndex() != -1:
            key = self.keys_box.currentText()
            self.data.set_message(self.path, self.localized, key, None)
            self.keys_box.removeItem(self.keys_box.currentIndex())

    def _on_rename(self):
        if self.keys_box.currentIndex() != -1:
            choice, ok = QInputDialog.getText(self, "Enter Key", "Key")
            if ok:
                # Verify that the key is unique.
                if not self._key_is_unique(choice):
                    self.message = QMessageBox()
                    self.message.setText(f"The key {choice} is already in use.")
                    self.message.exec_()
                    return
                key = self.keys_box.currentText()
                value = self.data.message(self.path, self.localized, key)
                self.data.set_message(self.path, self.localized, choice, value)
                self.data.set_message(self.path, self.localized, key, None)
                self.keys_box.setItemText(self.keys_box.currentIndex(), choice)

    def _key_is_unique(self, key) -> bool:
        return key not in self.data.enumerate_messages(self.path, self.localized)