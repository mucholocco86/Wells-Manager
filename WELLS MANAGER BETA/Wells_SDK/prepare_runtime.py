# -*- coding: utf-8 -*-
"""Prepare the Windows x64 Ren'Py runtime shipped with Wells Manager Beta.

The original SDK in the repository is never modified. This script builds a
throw-away, headless runtime containing only what the Wells SDK bridge needs
for lint, dialogue/translation generation, compilation and persistent cleanup.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MANAGER = HERE.parent
REPO = MANAGER.parent
SOURCE = REPO / "renpy-7.4.11-sdk"
OUTPUT = MANAGER / "build_runtime" / "renpy-7.4.11-sdk"

# SDK applications, examples and source/authoring material not exposed by
# Wells Manager. The compiled engine lives under renpy/ and lib/; module/ is
# Ren'Py's native-extension source tree and is not required at runtime.
EXCLUDE_TOP = {
    "doc",
    "gui",
    "launcher",
    "module",
    "tutorial",
    "the_question",
    "renpy.app",
    "renpy-32.exe",
    "renpy.sh",
}

# Wells Manager Beta is currently a Windows x64 application. Ren'Py's shared
# Python 2.7 library is retained, together with the x64 Windows runtime.
EXCLUDE_LIB = {
    "linux-i686",
    "linux-x86_64",
    "mac-x86_64",
    "windows-i686",
}

# The Wells bridge invokes only Ren'Py commands registered as headless
# operations. ANGLE/Direct3D, NVIDIA profile support, TTS helpers, updater
# binaries and the standalone Python launchers are therefore unnecessary.
# Every removal here is guarded by the real tutorial functional test in CI.
EXCLUDE_WINDOWS_X64 = {
    "d3dcompiler_47.dll",
    "libEGL.dll",
    "libGLESv2.dll",
    "nvdrs.dll",
    "python.exe",
    "pythonw.exe",
    "say.vbs",
    "zsync.exe",
    "zsyncmake.exe",
}


def directory_size(path):
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            total += item.stat().st_size
    return total


def mib(value):
    return value / (1024.0 * 1024.0)


def ignore(directory, names):
    directory = Path(directory).resolve()
    if directory == SOURCE.resolve():
        return [name for name in names if name in EXCLUDE_TOP]
    if directory == (SOURCE / "lib").resolve():
        return [name for name in names if name in EXCLUDE_LIB]
    if directory == (SOURCE / "lib" / "windows-x86_64").resolve():
        return [name for name in names if name in EXCLUDE_WINDOWS_X64]
    return []


def prune_paired_python_sources():
    """Drop .py engine/library sources only when the matching .pyo exists.

    Ren'Py 7.4.11's Windows release runtime ships optimized bytecode alongside
    sources. Wells does not expose engine development/debugging, so the source
    duplicate can be omitted. Game/common .rpy files are deliberately untouched.
    """
    count = 0
    saved = 0
    for root in (OUTPUT / "renpy", OUTPUT / "lib" / "python2.7"):
        if not root.is_dir():
            continue
        for source in list(root.rglob("*.py")):
            bytecode = source.with_suffix(".pyo")
            if bytecode.is_file():
                saved += source.stat().st_size
                source.unlink()
                count += 1
    return count, saved


def main():
    if not SOURCE.is_dir():
        raise SystemExit("SDK fonte não encontrado: {}".format(SOURCE))

    source_size = directory_size(SOURCE)

    if OUTPUT.parent.exists():
        shutil.rmtree(str(OUTPUT.parent))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(SOURCE), str(OUTPUT), ignore=ignore)

    pruned_sources, pruned_bytes = prune_paired_python_sources()

    required = [
        OUTPUT / "renpy.exe",
        OUTPUT / "renpy",
        OUTPUT / "renpy" / "translation",
        OUTPUT / "renpy" / "common",
        OUTPUT / "lib" / "python2.7",
        OUTPUT / "lib" / "windows-x86_64" / "libpython2.7.dll",
        OUTPUT / "lib" / "windows-x86_64" / "librenpython.dll",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Runtime reduzido incompleto: " + ", ".join(missing))

    forbidden = [
        OUTPUT / "launcher",
        OUTPUT / "doc",
        OUTPUT / "module",
        OUTPUT / "lib" / "linux-i686",
        OUTPUT / "lib" / "linux-x86_64",
        OUTPUT / "lib" / "mac-x86_64",
        OUTPUT / "lib" / "windows-i686",
    ]
    forbidden += [OUTPUT / "lib" / "windows-x86_64" / name for name in EXCLUDE_WINDOWS_X64]
    leftovers = [str(p) for p in forbidden if p.exists()]
    if leftovers:
        raise SystemExit("Itens removidos reapareceram no runtime: " + ", ".join(leftovers))

    output_size = directory_size(OUTPUT)
    saved = source_size - output_size

    print("Runtime Wells Beta preparado em:", OUTPUT)
    print("SDK/authoring removidos:", ", ".join(sorted(EXCLUDE_TOP)))
    print("Plataformas removidas:", ", ".join(sorted(EXCLUDE_LIB)))
    print("Binários Windows headless removidos:", ", ".join(sorted(EXCLUDE_WINDOWS_X64)))
    print("Fontes Python duplicadas removidas: {} ({:.2f} MiB)".format(pruned_sources, mib(pruned_bytes)))
    print("Tamanho SDK fonte: {:.2f} MiB".format(mib(source_size)))
    print("Tamanho runtime Wells: {:.2f} MiB".format(mib(output_size)))
    print("Redução bruta do runtime: {:.2f} MiB ({:.1f}%)".format(
        mib(saved), (100.0 * saved / source_size) if source_size else 0.0
    ))


if __name__ == "__main__":
    main()
