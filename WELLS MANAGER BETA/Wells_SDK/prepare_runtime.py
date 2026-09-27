# -*- coding: utf-8 -*-
"""Prepare the Windows x64 engine runtime shipped with Wells Manager Beta.

The upstream SDK in the repository is never modified. This script builds a
throw-away, headless runtime containing only what the Wells bridge needs for
lint, translation generation, compilation and persistent cleanup.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MANAGER = HERE.parent
REPO = MANAGER.parent
SOURCE = REPO / "renpy-7.4.11-sdk"
OUTPUT = MANAGER / "build_runtime" / "Wells_Runtime"

EXCLUDE_TOP = {
    "doc", "gui", "launcher", "module", "tutorial", "the_question",
    "renpy.app", "renpy-32.exe", "renpy.sh",
}

EXCLUDE_LIB = {"linux-i686", "linux-x86_64", "mac-x86_64", "windows-i686"}

# pythonw.exe is intentionally retained. The original Ren'Py 7.4.11 Launcher
# starts project commands through pythonw.exe -EO renpy.py, and Wells now
# reproduces that native command path instead of calling renpy.exe directly.
EXCLUDE_WINDOWS_X64 = {
    "d3dcompiler_47.dll", "libEGL.dll", "libGLESv2.dll", "nvdrs.dll",
    "python.exe", "say.vbs", "zsync.exe", "zsyncmake.exe",
}


def directory_size(path):
    total = 0
    for item in path.rglob("*"):
        if item.is_file(): total += item.stat().st_size
    return total


def mib(value): return value / (1024.0 * 1024.0)


def ignore(directory, names):
    directory = Path(directory).resolve()
    if directory == SOURCE.resolve(): return [name for name in names if name in EXCLUDE_TOP]
    if directory == (SOURCE / "lib").resolve(): return [name for name in names if name in EXCLUDE_LIB]
    if directory == (SOURCE / "lib" / "windows-x86_64").resolve(): return [name for name in names if name in EXCLUDE_WINDOWS_X64]
    return []


def patch_translation_source_scan():
    """Make translated language folders output-only during Wells generation.

    Ren'Py's generator already excludes tl/ when enumerating source files, but
    the engine parses scripts before that command runs. Wells skips translated
    language folders at that earlier stage. The special tl/None bootstrap tree
    is retained because some Ren'Py projects explicitly load modules from it.
    """
    script = OUTPUT / "renpy" / "script.py"
    text = script.read_text(encoding="utf-8")
    old = '''        for dir, fn in dirlist: # @ReservedAssignment\n\n            if fn.endswith(".rpy"):\n'''
    new = '''        wells_originals_only = os.environ.get("WELLS_TRANSLATE_ORIGINALS_ONLY", "") == "1"\n        tl_prefix = renpy.config.tl_directory.replace("\\\\", "/").strip("/") + "/"\n        tl_none_prefix = tl_prefix + "None/"\n\n        for dir, fn in dirlist: # @ReservedAssignment\n\n            # Wells Generate Translations ignores actual translated languages.\n            # tl/None is a Ren'Py bootstrap/module tree in some projects, not a\n            # user language translation, and therefore must remain loadable.\n            wells_fn = fn.replace("\\\\", "/")\n            if wells_originals_only and wells_fn.startswith(tl_prefix) and not wells_fn.startswith(tl_none_prefix):\n                continue\n\n            if fn.endswith(".rpy"):\n'''
    if old not in text:
        raise SystemExit("Ponto de patch do scanner Ren'Py 7.4.11 não encontrado.")
    script.write_text(text.replace(old, new, 1), encoding="utf-8")
    # pythonw.exe is launched with -O, so a stale script.pyo would take priority
    # over our runtime-only source patch.
    pyo = script.with_suffix(".pyo")
    if pyo.exists(): pyo.unlink()


def prune_paired_python_sources():
    count = 0; saved = 0
    for root in (OUTPUT / "renpy", OUTPUT / "lib" / "python2.7"):
        if not root.is_dir(): continue
        for source in list(root.rglob("*.py")):
            bytecode = source.with_suffix(".pyo")
            if bytecode.is_file():
                saved += source.stat().st_size; source.unlink(); count += 1
    return count, saved


def main():
    if not SOURCE.is_dir(): raise SystemExit("SDK fonte não encontrado: {}".format(SOURCE))
    source_size = directory_size(SOURCE)
    if OUTPUT.parent.exists(): shutil.rmtree(str(OUTPUT.parent))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(SOURCE), str(OUTPUT), ignore=ignore)
    patch_translation_source_scan()
    pruned_sources, pruned_bytes = prune_paired_python_sources()

    required = [
        OUTPUT / "renpy.exe", OUTPUT / "renpy.py", OUTPUT / "renpy", OUTPUT / "renpy" / "script.py",
        OUTPUT / "renpy" / "translation", OUTPUT / "renpy" / "common", OUTPUT / "lib" / "python2.7",
        OUTPUT / "lib" / "windows-x86_64" / "pythonw.exe",
        OUTPUT / "lib" / "windows-x86_64" / "libpython2.7.dll",
        OUTPUT / "lib" / "windows-x86_64" / "librenpython.dll",
        OUTPUT / "LICENSE.txt",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing: raise SystemExit("Runtime reduzido incompleto: " + ", ".join(missing))
    if (OUTPUT / "renpy" / "script.pyo").exists():
        raise SystemExit("script.pyo antigo não pode coexistir com o scanner Wells modificado.")

    forbidden = [
        OUTPUT / "launcher", OUTPUT / "doc", OUTPUT / "module",
        OUTPUT / "lib" / "linux-i686", OUTPUT / "lib" / "linux-x86_64",
        OUTPUT / "lib" / "mac-x86_64", OUTPUT / "lib" / "windows-i686",
    ]
    forbidden += [OUTPUT / "lib" / "windows-x86_64" / name for name in EXCLUDE_WINDOWS_X64]
    leftovers = [str(p) for p in forbidden if p.exists()]
    if leftovers: raise SystemExit("Itens removidos reapareceram no runtime: " + ", ".join(leftovers))

    output_size = directory_size(OUTPUT); saved = source_size - output_size
    print("Wells Runtime preparado em:", OUTPUT)
    print("Scanner Wells: idiomas em game/tl são somente saída durante Generate Translations; tl/None técnico é preservado.")
    print("SDK/authoring removidos:", ", ".join(sorted(EXCLUDE_TOP)))
    print("Plataformas removidas:", ", ".join(sorted(EXCLUDE_LIB)))
    print("Binários Windows headless removidos:", ", ".join(sorted(EXCLUDE_WINDOWS_X64)))
    print("Fontes Python duplicadas removidas: {} ({:.2f} MiB)".format(pruned_sources, mib(pruned_bytes)))
    print("Tamanho SDK fonte: {:.2f} MiB".format(mib(source_size)))
    print("Tamanho Wells Runtime: {:.2f} MiB".format(mib(output_size)))
    print("Redução bruta do runtime: {:.2f} MiB ({:.1f}%)".format(mib(saved), (100.0 * saved / source_size) if source_size else 0.0))


if __name__ == "__main__": main()
