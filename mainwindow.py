"""functions of the UI"""

import os
import zipfile

# -------------------- Import Lib Tier -------------------
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal, QThread

# -------------------- Import Lib User -------------------
from Ui_mainwindow import Ui_MainWindow
from api import steam_game_api, xdelta_api


PATH_PATCH = ".\\patch\\"
GAME_FOLDER_NAME = "GNOSIA"


# -------------------------------------------------------------------#
#                          CLASS WORKER                              #
# -------------------------------------------------------------------#
class _Worker(QObject):

    signal_apply_patch = pyqtSignal(str)
    signal_apply_patch_end = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

    def apply_patch_process(self, gamepath: str) -> None:

        def unzip_file(zip_path: str, extract_to: str) -> None:
            if not os.path.exists(zip_path):
                raise FileNotFoundError(f"Le fichier ZIP '{zip_path}' n'existe pas.")

            if not os.path.exists(extract_to):
                os.makedirs(extract_to)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

        zip_file: str = ""
        for file in os.listdir(PATH_PATCH):
            if file.endswith('.zip'):
                zip_file = os.path.join(PATH_PATCH, file)
                break

        if zip_file == "":
            raise FileNotFoundError("Aucun fichier ZIP trouvé dans le dossier source.")

        unzip_file(zip_file, gamepath)

        self.signal_apply_patch_end.emit()


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

    def find_steam_game_path(self) -> None:
        gamepath: str | int = steam_game_api.find_game_path(GAME_FOLDER_NAME)
        if isinstance(gamepath, str):
            self.ui.lineEdit_gamePath.setText(gamepath)

    @pyqtSlot()
    def find_element(self) -> None:
        """open the finder windows,
        put the path in the fileEdit
        """
        folder: str = QFileDialog.getExistingDirectory(self, "Choisir dossier jeu steam",
                                                  QDir.currentPath(), QFileDialog.ShowDirsOnly)
        self.ui.lineEdit_gamePath.setText(folder)
        self.ui.label_stateProcess.hide()

    @pyqtSlot()
    def run_process(self) -> None:
        self.ui.label_stateProcess.setText("application du patch...")
        self.ui.label_stateProcess.show()
        self.update_ui(False)
        self.m_worker.signal_apply_patch.emit(self.ui.lineEdit_gamePath.text())

    @pyqtSlot()
    def handle_apply_patch_result(self) -> None:
        self.ui.label_stateProcess.setText("patch appliqué !")
        self.update_ui(True)

    def update_ui(self, state: bool) -> None:
        self.ui.lineEdit_gamePath.setEnabled(state)
        self.ui.pushButton_browse.setEnabled(state)
        self.ui.pushButton_process.setEnabled(state)
