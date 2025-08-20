import os as _os
import shutil as _shutil
import winreg as _winreg
from pathlib import Path
from typing import Union, List


def find_steam_folder_path() -> Union[str, int]:
    """Find where steam is located on windows

    Returns:
        Union[str, int]: path of steam, or error code

    error code:
    -1 if path of steam not found in register
    """
    KEY_PATH_STEAM = r"SOFTWARE\\Valve\\Steam"
    KEY_NAME = "SteamPath"
    try:
        key_steam = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, KEY_PATH_STEAM, 0, _winreg.KEY_READ)
        return _winreg.QueryValueEx(key_steam, KEY_NAME)[0]
    except FileNotFoundError:
        return -1


def find_steam_library_folders_path() -> Union[List[str], int]:
    """Find every steam game library

    Returns:
        Union[List[str], int]: list with every library folders, or error code

    error code:
    -1 if path of steam not found in register
    -2 if libraryfolders.vdf not found
    """
    def __extract_path_in_textline(line: str) -> Union[str, None]:
        """find library path in a libraryfolders.vdf line

        Args:
            line (str): line of libraryfolders.vdf

        Returns:
            Union[str, None]: path of a game folder, or None if no path in the line
        """
        if "path" not in line:
            return None

        parts = line.split('"')
        if len(parts) >= 5:
            return parts[3].replace("\\\\", "\\")
        return None

    # Start of find_steam_library_folders
    steam_folder = find_steam_folder_path()
    if isinstance(steam_folder, int):
        return -1
    game_folders = []
    file_libraryfolders = Path(steam_folder) / "steamapps" / "libraryfolders.vdf"
    if file_libraryfolders.exists():
        with file_libraryfolders.open("r") as file:
            for line in file:
                path_library = __extract_path_in_textline(line)
                if path_library is not None:
                    game_folders.append(path_library)
    else:
        return -2
    return game_folders


def find_game_path(game_folder_name: str) -> Union[str, int]:
    """find path of a steam game

    Args:
        game_folder_name (str): exact name of the steam game folder in SteamLibrary\\steamapps\\common\\

    Returns:
        Union[str, int]: path of the folder game, or error code

    error code:
    -1 if path of steam not found in register
    -2 if libraryfolders.vdf not found
    -3 if game not found in steam libraries
    -4 game_folder_name not a string
    """
    if not isinstance(game_folder_name, str):
        return -4
    library_folders = find_steam_library_folders_path()
    if isinstance(library_folders, int):
        return library_folders

    EXTRA_PATH = Path("steamapps") / "common"
    for folder in library_folders:
        full_path = Path(folder) / EXTRA_PATH / game_folder_name
        if full_path.exists():
            return str(full_path)
    return -3


def copy_data_in_steam_game_folder(game_folder_name: str, data_to_copy: str, overwrite: bool = True) -> int:
    """copy file or folder in a specific steam game folder

    Args:
        game_folder_name (str): exact name of the steam game folder
        data_to_copy (str): file or folder to copy
        overwrite (bool, optional): overwrite or not if data already exists. Defaults to True.

    Returns:
        int: 0 if finished without error, error code if not 0

    error code:
    -1 if path of steam not found in register
    -2 if libraryfolders.vdf not found
    -3 if game not found in steam libraries
    -4 game_folder_name not a string
    -5 data_to_copy path does not exist
    """
    if not _os.path.exists(data_to_copy) or not isinstance(data_to_copy, str):
        return -5
    game_path = find_game_path(game_folder_name)
    if isinstance(game_path, int):
        return game_path
    if (_os.path.isfile(data_to_copy) and (overwrite or
       not _os.path.exists(_os.path.join(game_path, _os.path.basename(data_to_copy))))):
        _shutil.copy(data_to_copy, game_path)

    for root, _, files in _os.walk(data_to_copy):
        paste_folder = _os.path.join(game_path, root[len(data_to_copy):].lstrip("\\"))
        if not _os.path.exists(paste_folder):
            _os.makedirs(paste_folder)
        for file in files:
            if overwrite or not _os.path.exists(_os.path.join(paste_folder, file)):
                _shutil.copy(_os.path.join(root, file), paste_folder)
    return 0


def copy_data_from_steam_game_folder(game_folder_name: str, dest: str, data_to_copy: str = "", overwrite: bool = True) -> int:
    """copy file or folder from a specific steam game folder to a dest folder

    Args:
        game_folder_name (str): exact name of the steam game folder
        dest (str): folder where data will be copied
        data_to_copy (str, optional): file or folder in steam game folder to copy. Defaults to "", so whole game folder.
        overwrite (bool, optional): overwrite or not if data already exists. Defaults to True.

    Returns:
        int: 0 if finished without error, error code if not 0

    error code:
    -1 if path of steam not found in register
    -2 if libraryfolders.vdf not found
    -3 if game not found in steam libraries
    -4 game_folder_name not a string
    -5 dest path does not exist
    -6 data_to_copy not a string
    -7 data_to_copy does not exist
    """
    if not isinstance(game_folder_name, str):
        return -4
    if not isinstance(data_to_copy, str) or not _os.path.exists(data_to_copy):
        return -5

    game_path = find_game_path(game_folder_name)
    if isinstance(game_path, int):
        return game_path

    # If data_to_copy is a file
    if _os.path.isfile(data_to_copy):
        rel_path = _os.path.relpath(data_to_copy, _os.path.dirname(data_to_copy))
        dest_path = _os.path.join(game_path, rel_path)
        dest_dir = _os.path.dirname(dest_path)
        if not _os.path.exists(dest_dir):
            _os.makedirs(dest_dir)
        if overwrite or not _os.path.exists(dest_path):
            _shutil.copy2(data_to_copy, dest_path)
        return 0

    # If data_to_copy is a directory
    for root, _, files in _os.walk(data_to_copy):
        rel_dir = _os.path.relpath(root, data_to_copy)
        dest_dir = _os.path.join(game_path, rel_dir)
        if not _os.path.exists(dest_dir):
            _os.makedirs(dest_dir)
        for file in files:
            src_file = _os.path.join(root, file)
            dest_file = _os.path.join(dest_dir, file)
            if overwrite or not _os.path.exists(dest_file):
                _shutil.copy2(src_file, dest_file)

    return 0


def list_installed_games() -> Union[List[str], int]:
    """List all installed games in the Steam library

    Returns:
        Union[List[str], int]: list of installed games, or error code

    error code:
    -1 if path of steam not found in register
    -2 if libraryfolders.vdf not found
    """
    library_folders = find_steam_library_folders_path()
    if isinstance(library_folders, int):
        return library_folders

    installed_games = []
    EXTRA_PATH = Path("steamapps") / "common"
    for folder in library_folders:
        game_folder_path = Path(folder) / EXTRA_PATH
        if game_folder_path.exists():
            for game in game_folder_path.iterdir():
                if game.is_dir():
                    installed_games.append(game.name)
    return installed_games
