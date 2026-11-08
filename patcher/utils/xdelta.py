"""
File        : xdelta.py
Author      : Silous
Created on  : 2025-12-14
Description : functions to access to use xdelta

"""


# == Imports ==================================================================

import os
import subprocess
import sys
from logging import Logger

# -------------------- Import Lib User -------------------
from patcher.config import TOOL_FOLDER
from patcher.utils.logger import get_logger

# == Global Variables =========================================================

_logger: Logger = get_logger(__name__)
XDELTA_EXE = "xdelta3"
CREATION_FLAG = 0
if sys.platform == "win32":
    XDELTA_EXE = "xdelta3.exe"
    CREATION_FLAG = subprocess.CREATE_NO_WINDOW

XDELTA_PATH = os.path.join(TOOL_FOLDER, XDELTA_EXE)


# == Functions ================================================================


def apply_xdelta_patch(
    target_file: str,
    patch_file: str,
) -> bool:
    """
    Apply an xdelta3 patch and overwrite the original file.

    Args:
        target_file (str): Path to the file to patch
        patch_file (str): Path to the .xdelta patch file

    Returns:
        bool: True on success, False otherwise
    """

    if not os.path.isfile(XDELTA_PATH):
        _logger.error("xdelta3 executable not found at %s", XDELTA_PATH)
        return False

    if not os.path.isfile(target_file):
        _logger.error("Target file not found at %s", target_file)
        return False

    if not os.path.isfile(patch_file):
        _logger.error("Patch file not found at %s", patch_file)
        return False

    base, ext = os.path.splitext(target_file)
    temp_output = f"{base}.patched{ext}"

    command = [
        XDELTA_PATH,
        "-d",  # decode
        "-f",  # force overwrite
        "-s",
        target_file,
        patch_file,
        temp_output,
    ]

    process = subprocess.run(
        command,
        capture_output=True,
        creationflags=CREATION_FLAG,
        check=False,
    )

    if process.returncode != 0:
        _logger.error(
            "xdelta failed (code %d): %s",
            process.returncode,
            process.stderr.decode(errors="ignore").strip(),
        )
        return False

    try:
        os.replace(temp_output, target_file)
    except OSError as exc:
        _logger.error("Failed to overwrite original file %s: %s", target_file, exc)
        return False

    return True
