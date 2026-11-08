"""
File        : mainwindow_view.py
Author      : Silous
Created on  : 2025-10-05
Description : View of the main window
"""


# == Imports ==================================================================

# -------------------- Import Lib Tier -------------------
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

# -------------------- Import Lib User -------------------
from patcher import config
from patcher.ui import resources_rc  # type: ignore  # noqa: F401

# == Classes ==================================================================


class MainWindowView:
    def setupUi(self, mainwindow: QMainWindow) -> None:
        mainwindow.setWindowTitle(config.NAME_WINDOW)
        mainwindow.setWindowIcon(QIcon(":/gnosia-icon.ico"))

        # Central widget
        central_widget = QWidget(mainwindow)
        mainwindow.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Image game logo
        self.image_label = QLabel()
        pixmap = QPixmap(":/game-logo.jpg")
        pixmap = pixmap.scaled(
            400,
            200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label)

        # LineEdit with button
        line_layout = QHBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setMinimumWidth(600)
        self.button_browse = QPushButton("Parcourir")
        line_layout.addWidget(self.line_edit)
        line_layout.addWidget(self.button_browse)
        main_layout.addLayout(line_layout)

        process_layout = QHBoxLayout()
        self.spacer_process_1 = QSpacerItem(
            1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.button_process = QPushButton("Patcher")
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.progress_label.setFixedWidth(130)
        self.spacer_process_2 = QSpacerItem(
            1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        process_layout.addItem(self.spacer_process_1)
        process_layout.addWidget(self.button_process)
        process_layout.addWidget(self.progress_label)
        process_layout.addItem(self.spacer_process_2)
        main_layout.addLayout(process_layout)
