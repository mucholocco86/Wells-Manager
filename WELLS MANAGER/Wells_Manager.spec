# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

# Wells Manager: build único/portátil.
# Nesta fase o SDK 7.4.11 completo é incluído deliberadamente para validar as
# funções oficiais do Ren'Py. Depois da validação, o conjunto poderá ser
# reduzido com segurança sem adivinhar dependências.
hiddenimports = [
    'extractor_core', 'wells_translator_core', 'wells_revisor_core',
    'wells_base_linguistica', 'wells_guia_ptbr', 'wells_isolador_renpy',
    'sdk_core',
    'deobfuscate', 'decompiler', 'decompiler.astdump', 'decompiler.atldecompiler',
    'decompiler.magic', 'decompiler.renpycompat', 'decompiler.sl2decompiler',
    'decompiler.testcasedecompiler', 'decompiler.translate', 'decompiler.util',
    'argparse', 'glob', 'struct', 'zlib', 'base64', 'pickle', 'pickletools',
    'types', 'inspect', 'hashlib', 're', 'operator', 'io', 'contextlib',
    'copy', 'multiprocessing', 'xml', 'xml.etree', 'xml.etree.ElementTree',
    'xml.sax', 'xml.sax.saxutils', 'zipfile', 'tempfile', 'json', 'csv',
]
hiddenimports += collect_submodules('docx')

a = Analysis(
    ['main.py'],
    pathex=['.', 'Wells_Extractor', 'Wells_Extractor/unrpyc', 'Wells_Revisor', 'Wells_Translator', 'Wells_SDK'],
    binaries=[],
    datas=[
        ('wells.ico', '.'),
        ('Wells_Extractor', 'Wells_Extractor'),
        ('Wells_Translator', 'Wells_Translator'),
        ('Wells_Revisor', 'Wells_Revisor'),
        ('Wells_SDK', 'Wells_SDK'),
        ('../renpy-7.4.11-sdk', 'renpy-7.4.11-sdk'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Wells_Manager', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None, console=False,
    disable_windowed_traceback=False, argv_emulation=False, target_arch=None,
    codesign_identity=None, entitlements_file=None, icon=['wells.ico'],
)
