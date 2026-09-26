# -*- coding: utf-8 -*-
"""Laboratory validation for Wells' game-provided Ren'Py runtime detector."""
from __future__ import annotations

from pathlib import Path
import tempfile

import sdk_core


def make_game(root: Path, layout: str, name: str = 'SampleGame') -> Path:
    (root / 'game').mkdir(parents=True)
    (root / 'renpy').mkdir()
    py = root / 'lib' / layout / 'python.exe'
    py.parent.mkdir(parents=True)
    py.write_bytes(b'fake-python')
    exe = root / (name + '.exe')
    exe.write_bytes(b'fake-game')
    (root / (name + '.py')).write_text('# fake RenPy bootstrap\n', encoding='utf-8')
    return exe


def main() -> int:
    layouts = (
        ('py3-windows-x86_64', 'Python 3', '64-bit'),
        ('windows-x86_64', 'RenPy legado/compatível', '64-bit'),
        ('py2-windows-i686', 'Python 2', '32-bit'),
    )
    for layout, generation, architecture in layouts:
        with tempfile.TemporaryDirectory(prefix='wells-runtime-') as temp:
            root = Path(temp)
            exe = make_game(root, layout)
            info = sdk_core.select_game(exe)
            assert info['root'] == root.resolve()
            assert info['game_exe'] == exe.resolve()
            assert info['launcher'].name == 'SampleGame.py'
            assert info['layout'] == layout + '/python.exe'
            assert info['generation'] == generation
            assert info['architecture'] == architecture
            assert sdk_core._project_root(exe) == root.resolve()
            assert sdk_core.runtime_for(root)['game_exe'] == exe.resolve()

            # Keep this exact: it is the game-distribution invocation used by
            # renpy-translator and by real Ren'Py game bootstraps.
            command = sdk_core._command(info, root.resolve(), ['translate', 'brazil_teste', '--empty'])
            assert command[0] == str(info['python'])
            assert command[1] == '-O'
            assert command[2] == str(info['launcher'])
            assert command[3] == str(root.resolve())
            assert command[4:] == ['translate', 'brazil_teste', '--empty']
    print('Wells game-runtime detection OK: py3/py2, x64/x86 and optimized -O command validated.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
