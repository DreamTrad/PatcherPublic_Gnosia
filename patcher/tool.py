"""
File        : tool.py
Author      : Silous
Created on  : 2025-10-08
Description : call tool to repack the game.
"""

# == Imports ==================================================================

from logging import Logger
from pathlib import Path
import shutil
import subprocess

# -------------------- Import Lib User -------------------

from patcher import config
from patcher.utils import xdelta
from patcher.utils import steam
from patcher.utils.logger import get_logger


# == Global Variables =========================================================

_logger: Logger = get_logger(__name__)


# == Functions ================================================================

def repack() -> None:
    """whole patching process."""
    _call_repack()


def _call_repack() -> None:

    zip_file: Path = config.PATCH_FOLDER / "patch_data.zip"

    try:
        shutil.unpack_archive(str(zip_file), str(config.GAME_FOLDER))
    except Exception as exc:
        _logger.error("Failed to unzip patch %s: %s", zip_file, exc)