# -------------------- Import Lib Tier -------------------
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal, QThread

# -------------------- Import Lib User -------------------
from Ui_mainwindow import Ui_MainWindow
from api import steam_game_api, xdelta_api

import os


PATH_PATCH = ".\\patch\\"


# -------------------------------------------------------------------#
#                          CLASS WORKER                              #
# -------------------------------------------------------------------#
class _Worker(QObject):

    signal_apply_patch = pyqtSignal(str)
    signal_apply_patch_end = pyqtSignal()

    def __init__(self):
        super().__init__()

    def apply_patch_process(self, gamepath):
        self.apply_one_patch("ze1", "exe", gamepath)
        self.apply_one_patch("Launcher", "exe", gamepath)
        self.apply_one_patch("ze1_data", "bin", gamepath)
        self.signal_apply_patch_end.emit()

    def apply_one_patch(self, file, extension, gamepath):
        file_to_patch = os.path.join(gamepath, file + "." + extension)
        file_patch = os.path.join(PATH_PATCH, file + "_patch.xdelta")
        res = xdelta_api.apply_patch(file_to_patch, file_patch)
        print(res)


# -------------------------------------------------------------------#
#                         CLASS MAINWINDOW                           #
# -------------------------------------------------------------------#
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.m_thread = QThread()
        self.m_thread.start()
        self.m_worker = _Worker()
        self.m_worker.moveToThread(self.m_thread)

        self.set_up_connect()

        self.ui.label_stateProcess.hide()
        self.ui.label_stateProcess_2.hide()

        xdelta_api.define_xdelta_path(".\\xdelta\\")

        self.find_steam_game_path()

    def set_up_connect(self):
        self.m_worker.signal_apply_patch.connect(self.m_worker.apply_patch_process)
        self.ui.pushButton_browse.clicked.connect(self.find_element)
        self.ui.pushButton_process.clicked.connect(self.run_process)
        self.m_worker.signal_apply_patch_end.connect(self.handle_apply_patch_result)

    def find_steam_game_path(self):
        gamepath = steam_game_api.find_game_path("Zero Escape The Nonary Games")
        if isinstance(gamepath, str):
            self.ui.lineEdit_gamePath.setText(gamepath)
        else:
            self.ui.label_noGameFound.show()

    @pyqtSlot()
    def find_element(self):
        """open the finder windows,
        put the path in the fileEdit
        """
        folder = QFileDialog.getExistingDirectory(self, "Choisir dossier jeu steam",
                                                  QDir.currentPath(), QFileDialog.ShowDirsOnly)
        self.ui.lineEdit_gamePath.setText(folder)

    @pyqtSlot()
    def run_process(self):
        self.ui.label_stateProcess.show()
        self.ui.label_stateProcess_2.show()
        self.update_ui(False)
        self.m_worker.signal_apply_patch.emit(self.ui.lineEdit_gamePath.text())

    @pyqtSlot()
    def handle_apply_patch_result(self):
        self.ui.label_stateProcess.setText("patch appliqué !")
        self.ui.label_stateProcess_2.hide()
        self.update_ui(True)

    def update_ui(self, state: bool):
        self.ui.lineEdit_gamePath.setEnabled(state)
        self.ui.pushButton_browse.setEnabled(state)
        self.ui.pushButton_process.setEnabled(state)
