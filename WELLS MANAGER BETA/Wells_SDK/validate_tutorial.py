# -*- coding: utf-8 -*-
"""Functional validation of the Wells SDK bridge against Ren'Py's tutorial.

This script is used only by the Beta build laboratory. It copies the original
Ren'Py tutorial to a temporary directory and exercises the same Python bridge
called by the Wells Manager interface. The repository tutorial is never changed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from docx import Document

import sdk_core
import dialogue_roundtrip


def require(path: Path, message: str) -> None:
    if not path.exists():
        raise RuntimeError(message + " Ausente: " + str(path))


def log(message: str) -> None:
    print(message, flush=True)


def _verify_roundtrip_target(project, output_dir, result, marker):
    map_path = Path(result["map"])
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    first = payload["entries"][0]
    target = project / "game" / "tl" / payload["language"] / first["tl_file"]
    return payload, first, target


def _test_roundtrip_txt(project, output_dir):
    result = dialogue_roundtrip.prepare(project, "wells_roundtrip_txt", fmt="txt", output_dir=output_dir, include_strings=True, log=log)
    document = Path(result["document"])
    map_path = Path(result["map"])
    require(document, "Fluxo Wells TXT não criou documento.")
    require(map_path, "Fluxo Wells TXT não criou mapa JSON físico.")
    payload, first, target = _verify_roundtrip_target(project, output_dir, result, "WELLSROUNDTRIPTXT")
    if not first["serial"].startswith("W") or not first["serial"][1:].isalnum():
        raise RuntimeError("Serial Wells não é alfanumérico limpo.")
    lines = document.read_text(encoding="utf-8").splitlines()
    idx = lines.index(first["serial"])
    lines[idx + 1] = lines[idx + 1] + " WELLSROUNDTRIPTXT"
    document.write_text("\n".join(lines) + "\n", encoding="utf-8")
    injected = dialogue_roundtrip.inject(project, document, log=log)
    if "WELLSROUNDTRIPTXT" not in target.read_text(encoding="utf-8-sig"):
        raise RuntimeError("Fluxo Wells TXT não devolveu a tradução ao arquivo TL.")
    if map_path.exists():
        raise RuntimeError("Mapa Wells TXT não foi removido após sucesso confirmado.")
    log("[OK] Wells TAB + JSON + TXT ida/volta funcional: {} registros.".format(injected["entries"]))


def _test_roundtrip_docx(project, output_dir):
    result = dialogue_roundtrip.prepare(project, "wells_roundtrip_docx", fmt="docx", output_dir=output_dir, include_strings=True, log=log)
    document = Path(result["document"])
    map_path = Path(result["map"])
    require(document, "Fluxo Wells DOCX não criou documento.")
    require(map_path, "Fluxo Wells DOCX não criou mapa JSON físico.")
    payload, first, target = _verify_roundtrip_target(project, output_dir, result, "WELLSROUNDTRIPDOCX")
    doc = Document(str(document))
    paragraphs = doc.paragraphs
    index = next(i for i, p in enumerate(paragraphs) if p.text.strip().upper() == first["serial"].upper())
    paragraphs[index + 1].text = paragraphs[index + 1].text + " WELLSROUNDTRIPDOCX"
    doc.save(str(document))
    injected = dialogue_roundtrip.inject(project, document, log=log)
    if "WELLSROUNDTRIPDOCX" not in target.read_text(encoding="utf-8-sig"):
        raise RuntimeError("Fluxo Wells DOCX não devolveu a tradução ao arquivo TL.")
    if map_path.exists():
        raise RuntimeError("Mapa Wells DOCX não foi removido após sucesso confirmado.")
    log("[OK] Wells TAB + JSON + DOCX ida/volta funcional: {} registros.".format(injected["entries"]))


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
        output_dir = Path(temp) / "wells-output"
        output_dir.mkdir()
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

        strings_result = sdk_core.extract_string_translations(project, "wells_test", log=log)
        strings_file = Path(strings_result["file"])
        require(strings_file, "Extração de strings não criou o JSON Wells.")
        if strings_file.stat().st_size == 0:
            raise RuntimeError("JSON de strings foi criado vazio.")
        with strings_file.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        if not isinstance(parsed, dict):
            raise RuntimeError("JSON de strings não contém um objeto válido.")
        log("[OK] Extração de strings funcional: {} entradas.".format(len(parsed)))

        sdk_core.merge_string_translations(project, "wells_test", replace=False, log=log)
        log("[OK] Mesclagem de strings funcional.")
        sdk_core.merge_string_translations(project, "wells_test", replace=True, log=log)
        log("[OK] Mesclagem/substituição de strings funcional.")
        sdk_core.reverse_language(project, "wells_test", log=log)
        log("[OK] Inversão de strings funcional.")

        # New Wells bridge: Ren'Py TAB -> physical JSON -> clean document -> TL.
        _test_roundtrip_txt(project, output_dir)
        _test_roundtrip_docx(project, output_dir)

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
