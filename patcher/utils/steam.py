"""
File        : steam.py
Author      : Silous
Created on  : 2025-10-05
Description : functions to access steam game folders

"""


# == Imports ==================================================================

from logging import Logger
from pathlib import Path
import shutil
import winreg

# -------------------- Import Lib User -------------------

from patcher.utils.logger import get_logger


# == Global Variables =========================================================

_logger: Logger = get_logger(__name__)


# == Functions ================================================================

def find_steam_folder_path() -> str | None:
    """Find where Steam is installed on Windows.

    Returns:
        str: path of steam, or None if error
    """
    KEY_PATH_STEAM = r"SOFTWARE\\Valve\\Steam"
    KEY_NAME = "SteamPath"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH_STEAM, 0, winreg.KEY_READ) as key:
            return winreg.QueryValueEx(key, KEY_NAME)[0]
    except FileNotFoundError:
        _logger.error("Steam registry key not found.")
    except Exception as e:
        _logger.exception("Error reading Steam path from registry: %s", e)
    return None


def find_steam_library_folders_path() -> list[str] | None:
    """Find every Steam game library folder.

    Returns:
        list[str] | None: list with every library folder, or None if not found.
    """
    def extract_path_in_textline(line: str) -> str | None:
        """Extract library path from a line in libraryfolders.vdf."""
        if '"path"' not in line:
            return None
        parts: list[str] = line.split('"')
        if len(parts) >= 5:
            return parts[3].replace("\\\\", "\\")
        return None

    steam_folder: str | None = find_steam_folder_path()
    if not steam_folder:
        _logger.error("Steam installation path not found.")
        return None

    vdf_path: Path = Path(steam_folder) / "steamapps" / "libraryfolders.vdf"

    if not vdf_path.exists():
        _logger.error("libraryfolders.vdf not found at %s", vdf_path)
        return None

    game_folders: list[str] = []
    try:
        with vdf_path.open(encoding="utf-8") as file:
            for line in file:
                path_library: str | None = extract_path_in_textline(line)
                if path_library:
                    game_folders.append(path_library)
    except Exception as e:
        _logger.exception("Error while parsing libraryfolders.vdf: %s", e)
        return None

    return game_folders or None


def find_gamepath(game_folder_name: str) -> str | None:
    """Find the installation path of a Steam game.

    Args:
        game_folder_name (str): exact folder name of the Steam
        game inside `steamapps/common/`.

    Returns:
        str | None: Full path to the game folder, or None if not found.
    """
    library_folders: list[str] | None = find_steam_library_folders_path()
    if library_folders is None:
        _logger.error("Steam library folders could not be found.")
        return

    for folder in library_folders:
        gamepath: Path = Path(folder) / "steamapps" / "common" / game_folder_name
        if gamepath.exists():
            _logger.info("Found game '%s' at %s", game_folder_name, gamepath)
            return str(gamepath)

    _logger.warning("Game '%s' not found in any Steam library.", game_folder_name)
    return


def copy_data_in_steam_game_folder(
    game_folder_name: str,
    data_to_copy: str | Path,
    overwrite: bool = True
) -> bool:
    """Copy a file or folder into a Steam game folder.

    Args:
        game_folder_name (str): exact name of the Steam game folder.
        data_to_copy (str | Path): file or folder to copy.
        overwrite (bool, optional): overwrite existing files. Defaults to True.

    Returns:
        bool: True if copy succeeded, False otherwise.
    """
    data_to_copy = Path(data_to_copy)
    if not data_to_copy.exists():
        _logger.error("Data to copy does not exist: %s", data_to_copy)
        return False

    gamepath_str: str | None = find_gamepath(game_folder_name)
    if not gamepath_str:
        _logger.error("Game '%s' not found in Steam libraries.", game_folder_name)
        return False

    gamepath = Path(gamepath_str)

    try:
        if data_to_copy.is_file():
            dest: Path = gamepath / data_to_copy.name
            if overwrite or not dest.exists():
                shutil.copy(data_to_copy, dest)
                _logger.info("Copied file %s to %s", data_to_copy, dest)
        else:
            # copy folder recursively
            for src_path in data_to_copy.rglob("*"):
                relative_path: Path = src_path.relative_to(data_to_copy)
                dest_path: Path = gamepath / relative_path
                if src_path.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                else:
                    if overwrite or not dest_path.exists():
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(src_path, dest_path)
                        _logger.info("Copied file %s to %s", src_path, dest_path)
        return True
    except Exception as e:
        _logger.exception("Error copying data to game folder: %s", e)
        return False


def copy_data_from_steam_game_folder(
    game_folder_name: str,
    dest: str | Path,
    data_to_copy: str,
    overwrite: bool = True
) -> bool:
    """Copy file or folder from a Steam game folder to a destination folder.

    Args:
        game_folder_name (str): exact name of the Steam game folder.
        dest (str | Path): folder where data will be copied.
        data_to_copy (str, optional): file or folder inside the game folder to copy.
        overwrite (bool, optional): overwrite existing files. Defaults to True.

    Returns:
        bool: True if copy succeeded, False otherwise.
    """
    dest = Path(dest)
    if not dest.exists():
        _logger.error("Destination folder does not exist: %s", dest)
        return False

    gamepath_str: str | None = find_gamepath(game_folder_name)
    if not gamepath_str:
        _logger.error("Game '%s' not found in Steam libraries.", game_folder_name)
        return False

    gamepath = Path(gamepath_str)
    src_path: Path = gamepath / data_to_copy if data_to_copy else gamepath
    if not src_path.exists():
        _logger.error("Data to copy does not exist: %s", src_path)
        return False

    try:
        if src_path.is_file():
            dest_file: Path = dest / src_path.name
            if overwrite or not dest_file.exists():
                shutil.copy(src_path, dest_file)
                _logger.info("Copied file %s to %s", src_path, dest_file)
        else:
            # recursive copy for folders
            for src_item in src_path.rglob("*"):
                relative: Path = src_item.relative_to(src_path)
                dest_item: Path = dest / relative
                if src_item.is_dir():
                    dest_item.mkdir(parents=True, exist_ok=True)
                else:
                    dest_item.parent.mkdir(parents=True, exist_ok=True)
                    if overwrite or not dest_item.exists():
                        shutil.copy(src_item, dest_item)
                        _logger.info("Copied file %s to %s", src_item, dest_item)
        return True
    except Exception as e:
        _logger.exception("Error copying data from game folder: %s", e)
        return False
