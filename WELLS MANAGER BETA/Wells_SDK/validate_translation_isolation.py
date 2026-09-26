# -*- coding: utf-8 -*-
"""Regression test: unrelated existing TL files must not break new generation."""
from __future__ import annotations
import os, shutil, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import sdk_core


def main():
    if len(sys.argv)!=3:
        raise SystemExit('usage: validate_translation_isolation.py <runtime> <tutorial>')
    runtime=Path(sys.argv[1]).resolve(); tutorial=Path(sys.argv[2]).resolve()
    os.environ['WELLS_RENPY_SDK']=str(runtime)
    with tempfile.TemporaryDirectory(prefix='wells_tl_test_') as td:
        project=Path(td)/'tutorial_copy'
        shutil.copytree(str(tutorial),str(project))
        broken=project/'game'/'tl'/'brazil'/'strings.rpy'
        broken.parent.mkdir(parents=True,exist_ok=True)
        original='translate brazil strings:\n\n    new "Eu te amo, Sylph."\n'
        broken.write_text(original,encoding='utf-8')

        sdk_core.generate_translations(project,'wells_test',True,print)

        if broken.read_text(encoding='utf-8')!=original:
            raise SystemExit('FAIL: tradução preexistente foi alterada.')
        generated=project/'game'/'tl'/'wells_test'
        if not generated.is_dir() or not list(generated.rglob('*.rpy')):
            raise SystemExit('FAIL: nova tradução não foi gerada.')
        holds=list(project.glob('.wells_tl_hold_*'))
        if holds:
            raise SystemExit('FAIL: pasta temporária TL não foi restaurada: '+str(holds))
        print('OK: tradução nova gerada com TL preexistente incompatível preservado.')


if __name__=='__main__': main()
