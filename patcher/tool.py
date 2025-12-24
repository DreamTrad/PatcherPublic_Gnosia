"""
File        : tool.py
Author      : Silous
Created on  : 2025-10-08
Description : call tool to repack the game.
"""

# == Imports ==================================================================

from logging import Logger
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

    command: list[str] = [
        "tool.exe",
        "file.txt"
    ]

    subprocess.run(
        command,
        shell=True,
        check=False,
        cwd=config.TOOL_FOLDER
        )
