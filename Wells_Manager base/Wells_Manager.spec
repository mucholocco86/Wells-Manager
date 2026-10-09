# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

docx_datas, docx_binaries, docx_hiddenimports = collect_all('docx')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=docx_binaries,
    datas=[
        ('Wells_Extractor', 'Wells_Extractor'),
        ('Wells_Translator', 'Wells_Translator'),
        ('Wells_Revisor', 'Wells_Revisor'),
        ('wells.ico', '.'),
    ] + docx_datas,
    hiddenimports=docx_hiddenimports + [
        'Wells_Extractor.main',
        'Wells_Translator.wells_translator_core',
        'Wells_Revisor.wells_revisor_core',
        'wells_guia_ptbr', 'wells_isolador_renpy', 'wells_base_linguistica',
        'argparse', 'glob', 'struct', 'zlib', 'base64', 'pickletools',
        'types', 'inspect', 'hashlib', 're', 'operator', 'io', 'contextlib',
        'copy', 'multiprocessing',
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    noarchive=False, optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Wells_Manager', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None,
    console=False, disable_windowed_traceback=False,
    argv_emulation=False, target_arch=None, codesign_identity=None,
    entitlements_file=None, icon=['wells.ico'],
)
