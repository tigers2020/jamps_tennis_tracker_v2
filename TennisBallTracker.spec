# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('src/resources/images/icons', 'src/resources/images/icons'), ('src/resources/tests/images', 'src/resources/tests/images'), ('src/resources/tests', 'src/resources/tests'), ('src/resources/models', 'src/resources/models'), ('src/resources/videos', 'src/resources/videos'), ('src/resources/planned_features.json', 'src/resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
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
    icon=['src\\resources\\images\\icons\\play.png'],
)
