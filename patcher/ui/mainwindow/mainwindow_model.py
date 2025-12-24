"""
File        : mainwindow_model.py
Author      : Silous
Created on  : 2025-06-15
Description : Model for the main window of the application.
"""

# == Imports ==================================================================

from logging import Logger
import os

# -------------------- Import Lib Tier -------------------

from PySide6.QtCore import QThread, QObject, Signal

# -------------------- Import Lib User -------------------

from patcher import config
from patcher.tool import repack
from patcher.utils.logger import get_logger
from patcher.utils import steam


# == Global Variables =========================================================

_logger: Logger = get_logger(__name__)


# == Classes ==================================================================

class MainWindowModel(QObject):

    signal_process_started = Signal()
    signal_process_finished = Signal()
    signal_update_progress = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None

    def model_stop(self) -> None:
        self.stop_process()

    def get_path_game(self) -> str:
        if config.IS_STEAM_GAME:
            steam_folder: str | None = steam.find_gamepath(config.STEAM_FOLDER)
            if steam_folder is None:
                return ""
            else:
                return steam_folder
        else:
            return ""

    def is_path_game_valid(self, gamepath: str) -> bool:
        return os.path.isdir(gamepath)

    def run_process(self) -> None:
        self.signal_process_started.emit()

        self._thread = QThread()
        self._thread.run = self._process_task
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()

    def _process_task(self) -> None:
        self.signal_update_progress.emit("Application du patch…")
        repack()

    def _on_thread_finished(self) -> None:
        self.signal_update_progress.emit("fini")
        self.signal_process_finished.emit()
        self._thread = None

    def stop_process(self) -> None:
        """Manually stop the running process if possible."""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
