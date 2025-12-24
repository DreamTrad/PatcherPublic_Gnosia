"""
File        : main.py
Author      : Silous
Created on  : 2025-10-02
Description : Main entry point for the application.

This script initializes the application, sets up the main window, and starts the Qt event loop.
"""

# == Imports ==================================================================

import sys

from PySide6.QtWidgets import QApplication


# == Main Application =========================================================


if __name__ == "__main__":

    app = QApplication(sys.argv)

    from patcher.ui.mainwindow.mainwindow_controller import MainWindowController

    program = MainWindowController()

    program.show()
    sys.exit(app.exec())
