# -*- coding: utf-8 -*-
"""Prepare the Ren'Py runtime shipped with Wells Manager.

The source SDK remains untouched. This script creates a reduced copy containing
Ren'Py's engine/runtime while excluding SDK applications and documentation that
Wells Manager never exposes.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MANAGER = HERE.parent
REPO = MANAGER.parent
SOURCE = REPO / "renpy-7.4.11-sdk"
OUTPUT = MANAGER / "build_runtime" / "renpy-7.4.11-sdk"

# These are standalone SDK/authoring resources, not engine dependencies used by
# the Wells command bridge. Keep LICENSE.txt and all engine/runtime directories.
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


def ignore(directory, names):
    directory = Path(directory)
    if directory.resolve() == SOURCE.resolve():
        return [name for name in names if name in EXCLUDE_TOP]
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
        OUTPUT / "lib",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Runtime reduzido incompleto: " + ", ".join(missing))
    print("Runtime Wells preparado em:", OUTPUT)
    print("Removidos:", ", ".join(sorted(EXCLUDE_TOP)))


if __name__ == "__main__":
    main()
