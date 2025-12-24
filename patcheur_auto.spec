# -*- mode: python ; coding: utf-8 -*-


import os
import shutil
import sys

sys.path.append(os.path.abspath("."))

from patcher import config

exe_name = getattr(config, "EXE_NAME", "Patcheur Auto")

dist_dir = "dist"

def copy_folder(src: str, dst: str) -> None:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def remove_gitkeep(folder: str) -> None:
    gitkeep_path = os.path.join(folder, ".gitkeep")
    if os.path.isfile(gitkeep_path):
        os.remove(gitkeep_path)


if os.path.exists(dist_dir):
    tool_dst = os.path.join(dist_dir, "tool")
    patch_dst = os.path.join(dist_dir, "patch")

    copy_folder("tool", tool_dst)
    copy_folder("patch", patch_dst)

    remove_gitkeep(tool_dst)
    remove_gitkeep(patch_dst)

block_cipher = None


a = Analysis(
    ['patcher\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/dreamtrad-logo.png',
)
