# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    'Wells_Launcher', 'Wells_Launcher_Fixed',
    'extractor_core', 'wells_revisor_core', 'wells_base_linguistica',
    'wells_guia_ptbr', 'wells_isolador_renpy', 'sdk_core',
    'dialogue_roundtrip', 'dialogue_manager',
    'deobfuscate', 'decompiler', 'decompiler.astdump', 'decompiler.atldecompiler',
    'decompiler.magic', 'decompiler.renpycompat', 'decompiler.sl2decompiler',
    'decompiler.testcasedecompiler', 'decompiler.translate', 'decompiler.util',
    'argparse', 'glob', 'struct', 'zlib', 'base64', 'pickle', 'pickletools',
    'types', 'inspect', 'hashlib', 're', 'operator', 'io', 'contextlib',
    'copy', 'multiprocessing', 'xml', 'xml.etree', 'xml.etree.ElementTree',
    'xml.sax', 'xml.sax.saxutils', 'zipfile', 'tempfile', 'json', 'csv',
]
hiddenimports += collect_submodules('docx')

# Gerenciador still uses the existing dialogue backend internally. The physical
# runtime is therefore retained as a dependency, but no Ren'Py control block is
# exposed by this provisional launcher.
datas = [
    ('wells.ico', '.'),
    ('Wells_Extractor/extractor_core.py', 'Wells_Extractor'),
    ('Wells_Extractor/unrpyc', 'Wells_Extractor/unrpyc'),
    ('Wells_Revisor/wells_revisor_core.py', 'Wells_Revisor'),
    ('Wells_Revisor/wells_base_linguistica.py', 'Wells_Revisor'),
    ('Wells_Revisor/wells_guia_ptbr.py', 'Wells_Revisor'),
    ('Wells_Revisor/wells_isolador_renpy.py', 'Wells_Revisor'),
    ('Wells_Revisor/Palavras_PT-BR.txt', 'Wells_Revisor'),
    ('Wells_Revisor/dados_linguisticos/LICENSE_fserb_MIT.txt', 'Wells_Revisor/dados_linguisticos'),
    ('Wells_Revisor/dados_linguisticos/fserb_conjugacoes.txt', 'Wells_Revisor/dados_linguisticos'),
    ('Wells_Revisor/dados_linguisticos/fserb_icf.csv', 'Wells_Revisor/dados_linguisticos'),
    ('Wells_Revisor/dados_linguisticos/fserb_lexico.txt', 'Wells_Revisor/dados_linguisticos'),
    ('Wells_Revisor/dados_linguisticos/fserb_verbos.txt', 'Wells_Revisor/dados_linguisticos'),
    ('Wells_SDK/sdk_core.py', 'Wells_SDK'),
    ('Wells_SDK/dialogue_roundtrip.py', 'Wells_SDK'),
    ('Wells_SDK/dialogue_manager.py', 'Wells_SDK'),
]

a = Analysis(
    ['Wells_Launcher_Compact.py'],
    pathex=['.', 'Wells_Extractor', 'Wells_Extractor/unrpyc', 'Wells_Revisor', 'Wells_SDK'],
    binaries=[], datas=datas, hiddenimports=hiddenimports,
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='Wells_Manager', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, console=False,
    disable_windowed_traceback=False, argv_emulation=False, target_arch=None,
    codesign_identity=None, entitlements_file=None, icon=['wells.ico'],
    contents_directory='.',
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=True, upx_exclude=[],
    name='Wells_Manager',
)
