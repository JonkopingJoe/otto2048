# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

BASE_DIR = os.path.abspath(".")

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[
        (os.path.join(BASE_DIR, 'pics'), 'pics'),
        (os.path.join(BASE_DIR, 'sound'), 'sound'),
        (os.path.join(BASE_DIR, 'NotoSansCJK-Regular.ttc'), '.'),
    ],
    hiddenimports=collect_submodules('pygame'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    singlefile=True,
    icon='otto_icon.ico'
)

