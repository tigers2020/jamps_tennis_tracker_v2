# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Project path
PROJ_PATH = Path.cwd()

# Define resource paths
resources_path = PROJ_PATH / 'src' / 'resources'
images_path = resources_path / 'images'
videos_path = resources_path / 'videos'
models_path = resources_path / 'models'
resources_tests_path = resources_path / 'tests'
tests_path = PROJ_PATH / 'tests'

# Create list of data files to include
datas = [
    # Include images folder
    (str(images_path), 'src/resources/images'),
    
    # Include test images folder (used in calibration)
    (str(resources_tests_path), 'src/resources/tests'),
    (str(tests_path / 'images'), 'tests/images'),
    
    # Include videos folder
    (str(videos_path), 'src/resources/videos'),
    
    # Include models folder (optional)
    (str(models_path), 'src/resources/models'),
    
    # Other required resource files
    (str(resources_path / 'planned_features.json'), 'src/resources')
]

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TennisBallTracker',
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
    icon=str(images_path / 'icons' / 'play.png'),
) 