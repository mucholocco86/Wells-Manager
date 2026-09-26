# -*- coding: utf-8 -*-
"""Prepare the Windows x64 Ren'Py runtime shipped with Wells Manager Beta.

The original SDK in the repository is never modified. This script builds a
throw-away runtime containing the engine plus only the platform files needed by
the Windows 64-bit Wells Manager build.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MANAGER = HERE.parent
REPO = MANAGER.parent
SOURCE = REPO / "renpy-7.4.11-sdk"
OUTPUT = MANAGER / "build_runtime" / "renpy-7.4.11-sdk"

# SDK applications/authoring material not exposed by Wells Manager.
EXCLUDE_TOP = {
    "doc",
    "gui",
    "launcher",
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


def ignore(directory, names):
    directory = Path(directory).resolve()
    if directory == SOURCE.resolve():
        return [name for name in names if name in EXCLUDE_TOP]
    if directory == (SOURCE / "lib").resolve():
        return [name for name in names if name in EXCLUDE_LIB]
    return []


def main():
    if not SOURCE.is_dir():
        raise SystemExit("SDK fonte não encontrado: {}".format(SOURCE))
    if OUTPUT.parent.exists():
        shutil.rmtree(str(OUTPUT.parent))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(SOURCE), str(OUTPUT), ignore=ignore)

    required = [
        OUTPUT / "renpy.exe",
        OUTPUT / "renpy",
        OUTPUT / "renpy" / "translation",
        OUTPUT / "renpy" / "common",
        OUTPUT / "lib" / "python2.7",
        OUTPUT / "lib" / "windows-x86_64",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Runtime reduzido incompleto: " + ", ".join(missing))

    forbidden = [
        OUTPUT / "launcher",
        OUTPUT / "doc",
        OUTPUT / "lib" / "linux-i686",
        OUTPUT / "lib" / "linux-x86_64",
        OUTPUT / "lib" / "mac-x86_64",
        OUTPUT / "lib" / "windows-i686",
    ]
    leftovers = [str(p) for p in forbidden if p.exists()]
    if leftovers:
        raise SystemExit("Itens removidos reapareceram no runtime: " + ", ".join(leftovers))

    print("Runtime Wells Beta preparado em:", OUTPUT)
    print("SDK/authoring removidos:", ", ".join(sorted(EXCLUDE_TOP)))
    print("Plataformas removidas:", ", ".join(sorted(EXCLUDE_LIB)))


if __name__ == "__main__":
    main()
