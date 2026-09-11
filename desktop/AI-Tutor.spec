# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path


root = Path(SPECPATH)
assets = root / "assets"

a = Analysis(
    [str(root / "run.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(assets), "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "IPython", "PIL", "dateutil", "jedi", "jsonschema", "lark",
        "matplotlib", "nbformat", "notebook", "numpy", "pandas", "parso",
        "pkg_resources", "psutil", "pygments", "pytest", "rich", "scipy",
        "setuptools", "tkinter", "traitlets", "urllib3", "zmq",
    ],
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
    name="AI-Tutor",
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
    icon=[str(assets / "app.ico")],
)
