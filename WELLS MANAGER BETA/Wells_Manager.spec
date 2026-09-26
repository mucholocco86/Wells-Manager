# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

# O SDK fonte permanece intacto no repositório. O build usa somente a cópia
# reduzida preparada por Wells_SDK/prepare_runtime.py.
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

# Mantemos a arquitetura física dos módulos Wells dentro do onefile, mas sem
# empacotar README, caches, scripts de build/teste e cópias duplicadas. O
# dicionário PT-BR de 25 MB existe uma única vez e é compartilhado pelo Revisor
# e pela BaseLinguistica.
runtime_datas = [
    ('wells.ico', '.'),

    ('Wells_Extractor/extractor_core.py', 'Wells_Extractor'),
    ('Wells_Extractor/unrpyc', 'Wells_Extractor/unrpyc'),

    ('Wells_Translator/wells_translator_core.py', 'Wells_Translator'),

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
    ('build_runtime/renpy-7.4.11-sdk', 'renpy-7.4.11-sdk'),
]

a = Analysis(
    ['main.py'],
    pathex=['.', 'Wells_Extractor', 'Wells_Extractor/unrpyc', 'Wells_Revisor', 'Wells_Translator', 'Wells_SDK'],
    binaries=[],
    datas=runtime_datas,
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
