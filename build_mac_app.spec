# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['salary_calculator_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL._imaging',
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'openpyxl',
        'sqlite3',
        'datetime',
        'calendar',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pytest',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JatanSalaryApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JatanSalaryApp',
)

app = BUNDLE(
    coll,
    name='JatanSalaryApp.app',
    icon=None,
    bundle_identifier='com.jatanjewellery.salaryapp',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'Jatan Salary App',
        'CFBundleDisplayName': 'Jatan Salary Management',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': '© 2024 Jatan Jewellery',
    },
)

