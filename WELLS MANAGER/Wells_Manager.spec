# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

# Wells Manager: build único/portátil.
# As três ferramentas são carregadas a partir de subpastas, e o unrpyc é
# carregado dinamicamente em runtime. Por isso declaramos essas dependências
# explicitamente aqui, em vez de acumular --hidden-import no CMD.

hiddenimports = [
    'extractor_core',
    'wells_translator_core',
    'wells_revisor_core',
    'wells_base_linguistica',
    'wells_guia_ptbr',
    'wells_isolador_renpy',
    'deobfuscate',
    'decompiler',
    'decompiler.astdump',
    'decompiler.atldecompiler',
    'decompiler.magic',
    'decompiler.renpycompat',
    'decompiler.sl2decompiler',
    'decompiler.testcasedecompiler',
    'decompiler.translate',
    'decompiler.util',
    # imports da stdlib usados pelo motor carregado dinamicamente
    'argparse', 'glob', 'struct', 'zlib', 'base64', 'pickle', 'pickletools',
    'types', 'inspect', 'hashlib', 're', 'operator', 'io', 'contextlib',
    'copy', 'multiprocessing', 'xml', 'xml.etree', 'xml.etree.ElementTree',
    'xml.sax', 'xml.sax.saxutils', 'zipfile', 'tempfile', 'json', 'csv',
]
hiddenimports += collect_submodules('docx')

a = Analysis(
    ['main.py'],
    pathex=[
        '.',
        'Wells_Extractor',
        'Wells_Extractor/unrpyc',
        'Wells_Revisor',
        'Wells_Translator',
    ],
    binaries=[],
    datas=[
        ('wells.ico', '.'),
        ('Wells_Extractor', 'Wells_Extractor'),
        ('Wells_Translator', 'Wells_Translator'),
        ('Wells_Revisor', 'Wells_Revisor'),
    ],
    hiddenimports=hiddenimports,
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
    name='Wells_Manager',
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
    icon=['wells.ico'],
)
