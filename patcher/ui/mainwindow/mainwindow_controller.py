"""
File        : mainwindow.py
Author      : Silous
Created on  : 2025-10-02
Description : Main window of the application.
"""

# == Imports ==================================================================

# -------------------- Import Lib Tier -------------------
from PySide6.QtCore import QDir
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QFileDialog

# -------------------- Import Lib User -------------------

from patcher import config

from patcher.ui.mainwindow.mainwindow_view import MainWindowView
from patcher.ui.mainwindow.mainwindow_model import MainWindowModel


# == Classes ==================================================================

class MainWindowController(QMainWindow):
    def __init__(self) -> None:
        super(MainWindowController, self).__init__()
        self.ui = MainWindowView()
        self.model = MainWindowModel()
        self.ui.setupUi(self)

        self.set_up_connect()
        self.ui.line_edit.setText(self.model.get_path_game())

    def set_up_connect(self) -> None:
        # button
        self.ui.button_browse.clicked.connect(self.button_browse_clicked)
        self.ui.button_process.clicked.connect(self.button_proccess_clicked)
        # lineedit
        self.ui.line_edit.textChanged.connect(self.line_edit_text_changed)
        # signal
        self.model.signal_process_finished.connect(self.run_process_finished)
        self.model.signal_update_progress.connect(self.update_progress)

    # -------------------- Slots ----------------------------------------------

    def button_browse_clicked(self) -> None:
        folder: str = QFileDialog.getExistingDirectory(
            self, "Sélectionnez le dossier du jeu", QDir.currentPath(), QFileDialog.ShowDirsOnly  # type: ignore
            )
        if folder:
            self.ui.line_edit.setText(folder)

    def button_proccess_clicked(self) -> None:
        self.set_enable_state(False)
        config.GAME_FOLDER = self.ui.line_edit.text()
        self.model.run_process()

    def line_edit_text_changed(self) -> None:
        self.ui.button_process.setEnabled(self.model.is_path_game_valid(self.ui.line_edit.text()))

    def run_process_finished(self) -> None:
        self.set_enable_state(True)

    def update_progress(self, label: str) -> None:
        self.ui.progress_label.setText(label)

    # -------------------- Events ---------------------------------------------

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        """closeEvent override, stop the model

        Args:
            a0 (QCloseEvent | None): close event
        """
        self.model.model_stop()
        if a0 is not None:
            a0.accept()

    #   -------------------- Methods ------------------------------------------

    def set_enable_state(self, is_enabled: bool) -> None:
        self.ui.line_edit.setEnabled(is_enabled)
        self.ui.button_browse.setEnabled(is_enabled)
        self.ui.button_process.setEnabled(is_enabled)
