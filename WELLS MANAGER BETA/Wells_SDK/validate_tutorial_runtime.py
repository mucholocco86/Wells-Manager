# -*- coding: utf-8 -*-
"""Functional Wells validation against the real Ren'Py 7.4.11 tutorial.

This laboratory script is CI-only. The SDK is downloaded by GitHub Actions and
never enters the Wells executable. We copy the tutorial to a temporary project,
register the SDK runtime as if it were the runtime shipped by a game, and then
exercise Wells' public bridge functions.

The key regression creates an intentionally broken *unrelated* translation.
Ren'Py normally parses tl scripts during startup, so without Wells' isolation a
new translation fails on that unrelated file. The test proves that Wells hides
siblings, generates the requested language, and restores every existing file.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

import sdk_core


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def log(message):
    print(message, flush=True)


def digest_tree(root: Path, ignored=()):
    ignored = {x.casefold() for x in ignored}
    result = {}
    if not root.exists():
        return result
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0].casefold() in ignored:
            continue
        result[str(rel).replace('\\', '/')] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def register_sdk_runtime(project: Path, sdk: Path):
    python, layout = sdk_core._find_python(sdk)
    launcher = sdk / 'renpy.py'
    require(launcher.is_file(), 'SDK sem renpy.py.')
    runtime = {
        'root': project,
        'game_exe': sdk / 'renpy.exe',
        'launcher': launcher,
        'python': python,
        'layout': layout,
        'generation': 'Python 3' if 'py3-' in layout else ('Python 2' if 'py2-' in layout else 'RenPy legado/compatível'),
        'architecture': '64-bit' if 'x86_64' in layout else ('32-bit' if 'i686' in layout else 'Windows'),
    }
    sdk_core._SELECTED[sdk_core._norm(project)] = runtime
    return runtime


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit('Uso: validate_tutorial_runtime.py <renpy-sdk-root>')

    sdk = Path(sys.argv[1]).resolve()
    tutorial_source = sdk / 'tutorial'
    require((tutorial_source / 'game').is_dir(), 'Tutorial do SDK não encontrado.')

    with tempfile.TemporaryDirectory(prefix='wells-real-tutorial-') as temp:
        project = Path(temp) / 'tutorial'
        shutil.copytree(str(tutorial_source), str(project))
        runtime = register_sdk_runtime(project, sdk)
        log('Tutorial temporário: ' + str(project))
        log('Runtime real: lib/{}'.format(runtime['layout']))

        tl = project / 'game' / 'tl'
        target = 'wells_ci_test'
        broken = 'wells_broken_sibling'
        shutil.rmtree(tl / target, ignore_errors=True)
        shutil.rmtree(tl / broken, ignore_errors=True)

        baseline = digest_tree(tl, ignored=(target, broken))
        require(baseline, 'O tutorial do SDK não contém traduções existentes para o teste.')

        broken_dir = tl / broken
        broken_dir.mkdir(parents=True)
        broken_file = broken_dir / 'strings.rpy'
        broken_payload = (
            'translate wells_broken_sibling strings:\n\n'
            '    new "ESTA TRADUCAO E INTENCIONALMENTE INVALIDA"\n'
        ).encode('utf-8')
        broken_file.write_bytes(broken_payload)

        # This is the exact regression reported from a real game: generating a
        # new language must not parse/capture an unrelated tl/<other-language>.
        sdk_core.generate_translations(project, target, empty=True, log=log)
        generated = list((tl / target).rglob('*.rpy')) + list((tl / target).rglob('*.rpym'))
        require(generated, 'Gerar traduções não criou arquivos para o idioma solicitado.')
        require(broken_file.read_bytes() == broken_payload, 'Tradução irmã não foi restaurada byte-a-byte.')
        require(digest_tree(tl, ignored=(target, broken)) == baseline, 'Uma tradução preexistente do tutorial foi alterada.')
        log('[OK] Nova tradução ignora traduções irmãs e restaura game/tl sem alterações.')

        # Updating the requested language must keep that language visible to
        # Ren'Py, while still hiding every unrelated translation.
        sdk_core.generate_translations(project, target, empty=True, log=log)
        require(broken_file.read_bytes() == broken_payload, 'Atualização do idioma alvo alterou tradução irmã.')
        log('[OK] Atualização do próprio idioma preserva a semântica do RenPy.')

        # Source-dialogue export should use only the original game scripts.
        tab = sdk_core.extract_dialogue(project, fmt='tab', log=log)
        require(Path(tab['file']).is_file() and Path(tab['file']).stat().st_size > 0, 'dialogue.tab não foi gerado.')
        txt = sdk_core.extract_dialogue(project, fmt='txt', log=log)
        require(Path(txt['file']).is_file() and Path(txt['file']).stat().st_size > 0, 'dialogue.txt não foi gerado.')
        require(broken_file.read_bytes() == broken_payload, 'Extração de diálogo não restaurou tradução irmã.')
        log('[OK] Extração TAB/TXT trabalha sobre os scripts originais, sem capturar game/tl.')

        # Commands that intentionally operate on one language keep only that
        # target visible and therefore remain immune to malformed siblings.
        strings = sdk_core.extract_string_translations(project, target, log=log)
        require(Path(strings['file']).is_file() and Path(strings['file']).stat().st_size > 0, 'JSON de strings não foi criado.')
        sdk_core.merge_string_translations(project, target, replace=False, log=log)
        require(broken_file.read_bytes() == broken_payload, 'Operações de strings não restauraram tradução irmã.')
        log('[OK] Extrair/mesclar strings isola idiomas não relacionados.')

        # Lint/compile are deliberately whole-project operations. Remove the
        # synthetic broken sibling before testing them.
        shutil.rmtree(broken_dir)
        lint = sdk_core.lint(project, log=log)
        require(Path(lint['file']).is_file() and Path(lint['file']).stat().st_size > 0, 'Lint não produziu relatório.')
        sdk_core.force_recompile(project, log=log)
        require(list((project / 'game').rglob('*.rpyc')), 'Recompilação não produziu .rpyc.')
        sdk_core.delete_persistent(project, log=log)
        log('[OK] Lint, recompilação e persistentes executados no tutorial real.')

        require(digest_tree(tl, ignored=(target, broken)) == baseline, 'Arquivos de traduções originais mudaram após a bateria.')

    log('VALIDAÇÃO FUNCIONAL WELLS + TUTORIAL RENPY 7.4.11 CONCLUÍDA COM SUCESSO.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
