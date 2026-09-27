# -*- coding: utf-8 -*-
"""Regression test: existing/broken TL must not be input to Generate Translations."""
from __future__ import annotations
import os, shutil, sys, tempfile
from pathlib import Path
import sdk_core


def log(message): print(message, flush=True)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: validate_tl_isolation.py <runtime> <tutorial>")
    runtime=Path(sys.argv[1]).resolve(); tutorial=Path(sys.argv[2]).resolve()
    os.environ['WELLS_RENPY_SDK']=str(runtime)
    with tempfile.TemporaryDirectory(prefix='wells-tl-isolation-') as temp:
        project=Path(temp)/'tutorial'
        shutil.copytree(str(tutorial),str(project))
        broken=project/'game'/'tl'/'brazil'/'strings.rpy'
        broken.parent.mkdir(parents=True,exist_ok=True)
        # Deliberately reproduces the Nephilim failure class: `new` without
        # a preceding `old` in a translate strings block.
        broken.write_text('translate brazil strings:\n\n    new "Eu te amo, Sylph."\n',encoding='utf-8')
        log('TL inválida de controle criada: '+str(broken))
        sdk_core.generate_translations(project,'wells_isolation_test',empty=True,log=log)
        target=project/'game'/'tl'/'wells_isolation_test'
        files=list(target.rglob('*.rpy')) if target.is_dir() else []
        if not files:
            raise RuntimeError('A tradução nova não foi gerada com uma TL antiga inválida presente.')
        if not broken.is_file() or 'Eu te amo, Sylph.' not in broken.read_text(encoding='utf-8'):
            raise RuntimeError('A TL existente foi alterada durante o teste de isolamento.')
        log('[OK] game/tl foi ignorada como entrada e permaneceu fisicamente intacta.')
        log('[OK] Nova tradução criada somente a partir dos scripts originais: {} arquivos.'.format(len(files)))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
