# -*- coding: utf-8 -*-
"""Ren'Py command bridge used by Wells Manager.

Wells does not ship or execute its own Ren'Py SDK. The user selects the game's
Windows executable and this module discovers the Python/Ren'Py runtime already
shipped with that game. This follows the same general architecture proven by
Ren'Py translation tools that work against distributed games, while keeping
Wells' implementation independent.
"""
from __future__ import annotations

from collections import deque
from contextlib import contextmanager
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class SDKError(RuntimeError):
    pass


# Ren'Py has used several Windows runtime layouts over the years. Prefer the
# modern py3 layout, then the generic/py2 layouts used by older distributions.
_WINDOWS_PYTHON = (
    'py3-windows-x86_64/python.exe',
    'windows-x86_64/python.exe',
    'py2-windows-x86_64/python.exe',
    'py3-windows-i686/python.exe',
    'windows-i686/python.exe',
    'py2-windows-i686/python.exe',
)

_SELECTED = {}


def _norm(path):
    return os.path.normcase(str(Path(path).resolve()))


def _find_launcher(root, game_exe):
    """Find the bootstrap .py belonging to the selected game executable."""
    exact = root / (game_exe.stem + '.py')
    if exact.is_file():
        return exact

    wanted = game_exe.stem.casefold()
    for candidate in root.glob('*.py'):
        if candidate.stem.casefold() == wanted:
            return candidate

    # Some distributions rename the Windows executable while leaving a single
    # Ren'Py bootstrap script in the root. Only accept an unambiguous fallback.
    candidates = []
    for candidate in root.glob('*.py'):
        if candidate.name.lower() in ('setup.py',):
            continue
        candidates.append(candidate)
    if len(candidates) == 1:
        return candidates[0]
    raise SDKError(
        "Não foi possível identificar o bootstrap Ren'Py correspondente a '{}'.".format(game_exe.name))


def _find_python(root):
    lib = root / 'lib'
    for rel in _WINDOWS_PYTHON:
        candidate = lib / Path(rel)
        if candidate.is_file():
            return candidate, rel.replace('\\', '/')

    # Compatibility fallback for layouts not yet named above. Keep it narrow:
    # only Python executables directly inside a *windows* runtime directory.
    if lib.is_dir():
        found = []
        for candidate in lib.glob('*windows*/python.exe'):
            if candidate.is_file():
                found.append(candidate)
        if len(found) == 1:
            return found[0], str(found[0].relative_to(lib)).replace('\\', '/')
    raise SDKError(
        "O jogo possui a pasta 'lib', mas o runtime Python/Ren'Py para Windows não foi encontrado nela.")


def inspect_game(executable):
    """Validate a selected game .exe and describe its bundled Ren'Py runtime."""
    exe = Path(executable).expanduser().resolve()
    if not exe.is_file() or exe.suffix.lower() != '.exe':
        raise SDKError("Selecione o executável .exe principal do jogo Ren'Py.")
    root = exe.parent
    missing = [name for name in ('game', 'lib', 'renpy') if not (root / name).is_dir()]
    if missing:
        raise SDKError(
            "O executável selecionado não parece pertencer a uma distribuição Ren'Py completa. "
            "Pastas ausentes: {}.".format(', '.join(missing)))
    launcher = _find_launcher(root, exe)
    python, layout = _find_python(root)
    generation = 'Python 3' if ('py3-' in layout or (root / 'lib' / 'python3.9').exists()) else (
        'Python 2' if 'py2-' in layout else 'RenPy legado/compatível')
    architecture = '64-bit' if 'x86_64' in layout else ('32-bit' if 'i686' in layout else 'Windows')
    return {
        'root': root,
        'game_exe': exe,
        'launcher': launcher,
        'python': python,
        'layout': layout,
        'generation': generation,
        'architecture': architecture,
    }


def select_game(executable):
    """Register the exact executable chosen by the user for this Wells session."""
    runtime = inspect_game(executable)
    _SELECTED[_norm(runtime['root'])] = runtime
    return runtime


def _project_root(path):
    p = Path(path).expanduser().resolve()
    if p.is_file() and p.suffix.lower() == '.exe':
        return select_game(p)['root']
    if p.name.lower() == 'game' and p.is_dir():
        p = p.parent
    if not p.is_dir() or not (p / 'game').is_dir():
        raise SDKError("O projeto Ren'Py selecionado não possui uma pasta 'game' válida.")
    return p


def _autodetect_runtime(root):
    """Recover a runtime when an internal Wells call only has the project root."""
    cached = _SELECTED.get(_norm(root))
    if cached:
        return cached

    # Prefer executables that have a same-name .py bootstrap. This avoids
    # accidentally selecting uninstallers or helper executables.
    candidates = []
    for exe in sorted(root.glob('*.exe')):
        if (root / (exe.stem + '.py')).is_file():
            candidates.append(exe)
    if len(candidates) == 1:
        return select_game(candidates[0])
    if not candidates:
        raise SDKError(
            "O executável do jogo não está registrado. Use 'Selecionar projeto' e escolha o .exe principal do jogo.")
    raise SDKError(
        "Há mais de um executável Ren'Py possível nesta pasta. Use 'Selecionar projeto' e escolha o .exe correto.")


def runtime_for(project):
    root = _project_root(project)
    return _autodetect_runtime(root)


def _language(language, message='Informe o idioma da tradução.'):
    language = (language or '').strip()
    if not language or not all(c.islower() or c.isdigit() or c == '_' for c in language):
        raise SDKError(message + ' Use letras minúsculas, números ou underscore.')
    return language


def _translation_dir(project, language):
    return _project_root(project) / 'game' / 'tl' / language


def _strings_json(project, language):
    return _translation_dir(project, language) / 'strings.json'


def _format_strings_json(path):
    """Rewrite Ren'Py's compact JSON as a readable translator-friendly file."""
    path = Path(path)
    try:
        with path.open('r', encoding='utf-8') as handle:
            data = json.load(handle)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except Exception as exc:
        raise SDKError('As strings foram extraídas, mas o JSON não pôde ser organizado: {}'.format(exc))


@contextmanager
def _translation_scope(project, keep_language=None, log=None):
    """Hide unrelated game/tl entries while a translation command boots Ren'Py.

    Ren'Py's generator itself skips tl/* as source material, but the engine parses
    translation scripts during startup. A broken or third-party translation can
    therefore abort generation of an entirely different language. Wells keeps the
    requested language (when one exists), temporarily moves every unrelated tl
    entry outside game/, runs the command, and restores the game byte-for-byte.
    """
    project = _project_root(project)
    tl_dir = project / 'game' / 'tl'
    if not tl_dir.is_dir():
        yield
        return

    keep = keep_language.casefold() if keep_language else None
    children = [p for p in tl_dir.iterdir() if keep is None or p.name.casefold() != keep]
    if not children:
        yield
        return

    stash_root = Path(tempfile.mkdtemp(prefix='.wells_tl_stash_', dir=str(project)))
    stash = stash_root / 'tl'
    stash.mkdir()
    moved = []
    restored = False

    try:
        for child in children:
            held = stash / child.name
            shutil.move(str(child), str(held))
            moved.append((child, held))
        if log:
            if keep_language:
                log("Wells: traduções não relacionadas isoladas temporariamente; mantendo apenas tl/{} durante esta operação.".format(keep_language))
            else:
                log("Wells: pasta game/tl isolada temporariamente para trabalhar somente com os scripts originais do jogo.")
        yield
    finally:
        conflicts = []
        for original, held in reversed(moved):
            if not held.exists():
                continue
            if original.exists():
                conflicts.append(str(original))
                continue
            shutil.move(str(held), str(original))
        restored = not conflicts
        if restored:
            shutil.rmtree(stash_root, ignore_errors=True)
            if log:
                log("Wells: traduções existentes restauradas sem alterações.")
        else:
            raise SDKError(
                "O Ren'Py criou arquivos que conflitam com traduções temporariamente isoladas. "
                "Para proteger os dados, o Wells não sobrescreveu nada. Cópia preservada em: {}. "
                "Conflitos: {}".format(stash_root, ', '.join(conflicts)))


def _command(runtime, project, args):
    # A distributed Ren'Py game contains the same bootstrap arrangement used by
    # the SDK: bundled Python + the game's bootstrap .py + basedir + command.
    return [
        str(runtime['python']),
        str(runtime['launcher']),
        str(project),
    ] + [str(x) for x in args]


def run(project, args, log=None):
    project = _project_root(project)
    runtime = runtime_for(project)
    args = [str(x) for x in args]
    cmd = _command(runtime, project, args)
    if log:
        log("Ren'Py do jogo: " + ' '.join(args))
        log("Runtime: lib/{} ({}, {})".format(runtime['layout'], runtime['generation'], runtime['architecture']))

    startup = None
    creationflags = 0
    if os.name == 'nt':
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

    # Keep only a small diagnostic tail in memory. Long Ren'Py reports are
    # streamed to the Wells log instead of being duplicated indefinitely.
    tail = deque(maxlen=40)
    proc = subprocess.Popen(
        cmd,
        cwd=str(project),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        errors='replace',
        startupinfo=startup,
        creationflags=creationflags,
    )
    for line in proc.stdout:
        line = line.rstrip('\r\n')
        tail.append(line)
        if log and line:
            log(line)
    code = proc.wait()
    if code:
        diagnostic = '\n'.join(tail).strip()
        raise SDKError(diagnostic or "O Ren'Py do jogo encerrou a operação com erro (código {}).".format(code))
    return {
        'project': str(project),
        'command': args,
        'output_tail': list(tail),
        'runtime': str(runtime['python']),
        'game_exe': str(runtime['game_exe']),
    }


def generate_translations(project, language, empty=True, log=None):
    project = _project_root(project)
    language = _language(language, 'Informe o idioma.')
    args = ['translate', language]
    if language == 'rot13':
        args.append('--rot13')
    elif language == 'piglatin':
        args.append('--piglatin')
    elif empty:
        args.append('--empty')
    with _translation_scope(project, keep_language=language, log=log):
        return run(project, args, log)


def extract_string_translations(project, language, log=None, destination=None):
    project = _project_root(project)
    language = _language(language)
    destination = Path(destination).expanduser().resolve() if destination else _strings_json(project, language)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with _translation_scope(project, keep_language=language, log=log):
        result = run(project, ['extract_strings', language, str(destination)], log)
    _format_strings_json(destination)
    if log:
        log('Strings organizadas em: ' + str(destination))
    result['file'] = str(destination)
    return result


def merge_string_translations(project, language, replace=False, log=None, source=None, reverse=False):
    project = _project_root(project)
    language = _language(language)
    source = Path(source).expanduser().resolve() if source else _strings_json(project, language)
    if not source.is_file():
        raise SDKError("Arquivo de strings não encontrado: {}. Use 'Extrair strings' primeiro.".format(source))
    args = ['merge_strings', language, str(source)]
    if reverse:
        args.append('--reverse')
    if replace:
        args.append('--replace')
    with _translation_scope(project, keep_language=language, log=log):
        result = run(project, args, log)
    result['file'] = str(source)
    return result


def reverse_language(project, language, log=None):
    return merge_string_translations(project, language, replace=False, log=log, reverse=True)


def update_launcher_translations(project, log=None):
    project = _project_root(project)
    with _translation_scope(project, keep_language='None', log=log):
        return run(project, ['translate', 'None'], log)


def extract_dialogue(project, fmt='tab', strings=False, notags=False, escape=False, log=None):
    project = _project_root(project)
    if fmt not in ('tab', 'txt'):
        raise SDKError('Formato de diálogo inválido.')
    args = ['dialogue']
    if fmt == 'txt':
        args.append('--text')
    if strings:
        args.append('--strings')
    if notags:
        args.append('--notags')
    if escape:
        args.append('--escape')
    with _translation_scope(project, keep_language=None, log=log):
        result = run(project, args, log)
    result['file'] = str(project / ('dialogue.txt' if fmt == 'txt' else 'dialogue.tab'))
    return result


def lint(project, log=None):
    project = _project_root(project)
    report = project / 'wells_lint.txt'
    result = run(project, ['lint', str(report)], log)
    result['file'] = str(report)
    return result


def delete_persistent(project, log=None):
    return run(project, ['rmpersistent'], log)


def force_recompile(project, log=None):
    return run(project, ['compile'], log)
