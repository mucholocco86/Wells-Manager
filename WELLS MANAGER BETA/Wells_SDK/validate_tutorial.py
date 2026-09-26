# -*- coding: utf-8 -*-
"""Functional validation of the Wells SDK bridge against Ren'Py's tutorial.

This script is used only by the Beta build laboratory. It copies the original
Ren'Py tutorial to a temporary directory and exercises the same Python bridge
called by the Wells Manager interface. The repository tutorial is never changed.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys
import tempfile

import sdk_core


def require(path: Path, message: str) -> None:
    if not path.exists():
        raise RuntimeError(message + " Ausente: " + str(path))


def log(message: str) -> None:
    print(message, flush=True)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Uso: validate_tutorial.py <sdk_reduzido> <tutorial_original>")

    sdk = Path(sys.argv[1]).resolve()
    tutorial_source = Path(sys.argv[2]).resolve()
    require(sdk / "renpy.exe", "Runtime reduzido sem renpy.exe.")
    require(tutorial_source / "game", "Tutorial original inválido.")

    os.environ["WELLS_RENPY_SDK"] = str(sdk)

    with tempfile.TemporaryDirectory(prefix="wells-renpy-tutorial-") as temp:
        project = Path(temp) / "tutorial"
        shutil.copytree(str(tutorial_source), str(project))
        log("Projeto de teste: " + str(project))

        lint_result = sdk_core.lint(project, log=log)
        lint_file = Path(lint_result["file"])
        require(lint_file, "Lint executou sem produzir wells_lint.txt.")
        if lint_file.stat().st_size == 0:
            raise RuntimeError("wells_lint.txt foi criado vazio.")
        log("[OK] Lint funcional.")

        tab_result = sdk_core.extract_dialogue(project, fmt="tab", log=log)
        tab_file = Path(tab_result["file"])
        require(tab_file, "Extração de diálogos TAB não produziu dialogue.tab.")
        if tab_file.stat().st_size == 0:
            raise RuntimeError("dialogue.tab foi criado vazio.")
        log("[OK] Extração de diálogos TAB funcional.")

        txt_result = sdk_core.extract_dialogue(project, fmt="txt", log=log)
        txt_file = Path(txt_result["file"])
        require(txt_file, "Extração de diálogos TXT não produziu dialogue.txt.")
        if txt_file.stat().st_size == 0:
            raise RuntimeError("dialogue.txt foi criado vazio.")
        log("[OK] Extração de diálogos TXT funcional.")

        sdk_core.generate_translations(project, "wells_test", empty=True, log=log)
        translation_dir = project / "game" / "tl" / "wells_test"
        require(translation_dir, "Geração de traduções não criou game/tl/wells_test.")
        translation_files = list(translation_dir.rglob("*.rpy"))
        if not translation_files:
            raise RuntimeError("Geração de traduções não criou arquivos .rpy.")
        log("[OK] Geração de traduções funcional: {} arquivos.".format(len(translation_files)))

        # Remove pre-existing compiled scripts copied with the tutorial so this
        # check proves the compile command itself generated fresh bytecode.
        for compiled in (project / "game").rglob("*.rpyc"):
            compiled.unlink()
        sdk_core.force_recompile(project, log=log)
        compiled_files = list((project / "game").rglob("*.rpyc"))
        if not compiled_files:
            raise RuntimeError("Forçar recompilação não produziu arquivos .rpyc.")
        log("[OK] Forçar recompilação funcional: {} arquivos.".format(len(compiled_files)))

        sdk_core.delete_persistent(project, log=log)
        log("[OK] Eliminar dados persistentes executou sem erro.")

    log("VALIDAÇÃO WELLS BETA CONCLUÍDA COM SUCESSO.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
