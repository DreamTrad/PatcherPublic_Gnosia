"""functions of the UI"""

import os
import zipfile
import shutil

# -------------------- Import Lib Tier -------------------
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal, QThread

# -------------------- Import Lib User -------------------
from Ui_mainwindow import Ui_MainWindow
from api import steam_game_api
import debug

PATH_PATCH = "./patch/"

GAME_FOLDER_NAME = "PARANORMASIGHT"

SHAREDASSET = "PARANORMASIGHT_Data/sharedassets0.assets"
DATA_FOLDER = "PARANORMASIGHT_Data/"
ASSET_FOLDER = "PARANORMASIGHT_Data/StreamingAssets"


# -------------------------------------------------------------------#
#                          CLASS WORKER                              #
# -------------------------------------------------------------------#
class _Worker(QObject):

    signal_apply_patch = pyqtSignal(str)
    signal_apply_patch_end = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

    def apply_patch_process(self, gamepath: str) -> None:

        error: str = ""

        def unzip_file(zip_path: str, extract_to: str) -> str:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return ""

        zip_file: str = ""
        if not os.path.exists(PATH_PATCH):
            error = 'dossier "patch" non présent'
            self.signal_apply_patch_end.emit(error)
            return
        for file in os.listdir(PATH_PATCH):
            if file.endswith('.zip'):
                zip_file = os.path.join(PATH_PATCH, file)
                break

        if zip_file == "":
            debug.logging.info("Aucun fichier ZIP trouvé dans le dossier source.")
            error = 'patch non présent dans le dossier "patch"'
        else:
            error = unzip_file(zip_file, os.path.join(gamepath, ASSET_FOLDER))

        shutil.copy(os.path.join(PATH_PATCH, SHAREDASSET), os.path.join(gamepath, DATA_FOLDER))
        self.signal_apply_patch_end.emit(error)


# -------------------------------------------------------------------#
#                         CLASS MAINWINDOW                           #
# -------------------------------------------------------------------#
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.m_thread = QThread()
        self.m_thread.start()
        self.m_worker = _Worker()
        self.m_worker.moveToThread(self.m_thread)

        self.set_up_connect()

        self.ui.label_stateProcess.hide()

        self.find_steam_game_path()

    def set_up_connect(self) -> None:
        self.m_worker.signal_apply_patch.connect(self.m_worker.apply_patch_process)
        self.ui.pushButton_browse.clicked.connect(self.find_element)
        self.ui.pushButton_process.clicked.connect(self.run_process)
        self.m_worker.signal_apply_patch_end.connect(self.handle_apply_patch_result)
        self.ui.lineEdit_gamePath.textChanged.connect(self.on_game_path_changed)

    def find_steam_game_path(self) -> None:
        gamepath: str | int = steam_game_api.find_game_path(GAME_FOLDER_NAME)
        if isinstance(gamepath, str):
            self.ui.lineEdit_gamePath.setText(gamepath)
        else:
            self.ui.pushButton_process.setEnabled(False)
            debug.logging.info("probleme avec find_game_path, error : " + str(gamepath))

    @pyqtSlot()
    def find_element(self) -> None:
        """open the finder windows,
        put the path in the fileEdit
        """
        folder: str = QFileDialog.getExistingDirectory(self, "Choisir dossier jeu steam",
                                                  QDir.currentPath(), QFileDialog.ShowDirsOnly)
        self.ui.lineEdit_gamePath.setText(folder)
        self.ui.label_stateProcess.hide()
        if len(self.ui.lineEdit_gamePath.text()) == 0 or not os.path.exists(self.ui.lineEdit_gamePath.text()):
            self.ui.pushButton_process.setEnabled(False)
        else:
            self.ui.pushButton_process.setEnabled(True)

    @pyqtSlot(str)
    def on_game_path_changed(self, new_text: str) -> None:
        if len(new_text) == 0 or not os.path.exists(new_text):
            self.ui.pushButton_process.setEnabled(False)
        else:
            self.ui.pushButton_process.setEnabled(True)

    @pyqtSlot()
    def run_process(self) -> None:
        self.ui.label_stateProcess.setText("application du patch...")
        self.ui.label_stateProcess.show()
        self.update_ui(False)
        self.m_worker.signal_apply_patch.emit(self.ui.lineEdit_gamePath.text())

    @pyqtSlot(str)
    def handle_apply_patch_result(self, error: str) -> None:
        if error == "":
            self.ui.label_stateProcess.setText("patch appliqué !")
        else:
            self.ui.label_stateProcess.setText(error)
        self.update_ui(True)


    def update_ui(self, state: bool) -> None:
        self.ui.lineEdit_gamePath.setEnabled(state)
        self.ui.pushButton_browse.setEnabled(state)
        self.ui.pushButton_process.setEnabled(state)
