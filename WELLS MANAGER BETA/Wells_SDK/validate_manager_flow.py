# -*- coding: utf-8 -*-
from __future__ import annotations
import os, shutil, sys, tempfile
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit('usage: validate_manager_flow.py <runtime-sdk> <tutorial-project>')

runtime = Path(sys.argv[1]).resolve()
tutorial = Path(sys.argv[2]).resolve()
os.environ['WELLS_RENPY_SDK'] = str(runtime)

import dialogue_manager


def one(fmt, blocks):
    with tempfile.TemporaryDirectory(prefix='wells-manager-flow-') as tmp:
        root = Path(tmp)
        project = root / 'tutorial'
        output = root / 'output'
        shutil.copytree(tutorial, project)
        output.mkdir()
        result = dialogue_manager.prepare(
            project, 'wells_manager_test', fmt=fmt, blocks=blocks,
            output_dir=output, include_strings=True)
        assert result['entries'] > 0
        assert result['blocks'] >= 1
        assert dialogue_manager.map_path(output).is_file()
        assert (output / 'Wells_Temp' / 'dialogue.tab').is_file()
        assert not (project / 'dialogue.tab').exists()
        for document in result['documents']:
            assert Path(document).is_file()
        injected = dialogue_manager.inject(project, output, fmt, blocks=blocks)
        assert injected['entries'] == result['entries']
        assert injected['files'] > 0
        assert not dialogue_manager.map_path(output).exists()
        print('OK', fmt, 'blocks' if blocks else 'full', result['entries'], result['blocks'])


def main():
    for fmt in ('txt', 'docx'):
        for blocks in (False, True):
            one(fmt, blocks)
    print('Wells Manager TAB+JSON document roundtrip OK.')


if __name__ == '__main__':
    main()
