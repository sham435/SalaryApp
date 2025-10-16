# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_all

# Collect all numpy, pandas, and PIL modules
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all('pandas')
pillow_datas, pillow_binaries, pillow_hiddenimports = collect_all('PIL')

# Filter out .md files from collected datas
def filter_md_files(datas):
    """Remove any .md files from the datas list"""
    return [(src, dst) for src, dst in datas if not src.lower().endswith('.md')]

filtered_numpy_datas = filter_md_files(numpy_datas)
filtered_pandas_datas = filter_md_files(pandas_datas)
filtered_pillow_datas = filter_md_files(pillow_datas)

a = Analysis(
    ['salary_calculator_gui.py'],
    pathex=[],
    binaries=numpy_binaries + pandas_binaries + pillow_binaries,
    datas=filtered_numpy_datas + filtered_pandas_datas + filtered_pillow_datas,
    hiddenimports=numpy_hiddenimports + pandas_hiddenimports + pillow_hiddenimports + [
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
        '*.md',
        '*.MD',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JatanSalaryApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='installers/windows/jatan_icon.ico',  # Using your existing icon!
)

