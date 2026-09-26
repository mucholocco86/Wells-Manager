# -*- coding: utf-8 -*-
"""
Wells Translator - núcleo TXT/DOCX

Trabalha sobre arquivos .rpy já gerados em game/tl pelo Ren'Py.
Não cria TL, não altera idioma e não usa manifesto/JSON para o modo manual.
"""
from __future__ import annotations

import ast
import io
import zipfile
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET
import re
from pathlib import Path

from docx import Document


FULL_OLD_TXT = "old.txt"
FULL_NEW_TXT = "new.txt"
FULL_OLD_DOCX = "old.docx"
FULL_NEW_DOCX = "new.docx"

_QUOTED = re.compile(r'"((?:\\.|[^"\\])*)"')
_TRANSLATE = re.compile(
    r'^\s*translate\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+|strings)\s*:\s*$'
)
_OLD = re.compile(r'^\s*old\s+(".*")\s*$')
_NEW = re.compile(r'^\s*new\s+(".*")\s*$')


def _notify(progress, value, text=None):
    if progress:
        progress(max(0.0, min(100.0, float(value))), text)


def _read_text(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def _write_text(path: Path, text: str, bom: bool = False):
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


def _decode_quoted(token: str) -> str:
    return ast.literal_eval(token)


def _quote_renpy(text: str) -> str:
    return '"' + (
        text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\r", "\\r")
            .replace("\n", "\\n")
    ) + '"'


def _extract_last_string(line: str):
    matches = list(_QUOTED.finditer(line))
    if not matches:
        return None
    m = matches[-1]
    return _decode_quoted(m.group(0)), m.start(), m.end()


def _replace_last_string(line: str, new_text: str) -> str:
    found = _extract_last_string(line)
    if not found:
        raise ValueError("Linha Ren'Py sem texto reconhecível.")
    _, start, end = found
    return line[:start] + _quote_renpy(new_text) + line[end:]


def list_rpy(tl_dir):
    root = Path(tl_dir).resolve()
    return sorted(p for p in root.rglob("*.rpy") if p.is_file())


def scan_file(path: Path, root: Path):
    """Retorna registros traduzíveis na ordem em que aparecem no arquivo."""
    text, bom = _read_text(path)
    lines = text.splitlines(keepends=True)

    entries = []
    language = None
    block = None
    is_strings = False
    i = 0

    while i < len(lines):
        raw = lines[i].rstrip("\r\n")
        tm = _TRANSLATE.match(raw)

        if tm:
            language = tm.group(1)
            block = tm.group(2)
            is_strings = block == "strings"
            i += 1
            continue

        if language and is_strings:
            om = _OLD.match(raw)
            if om:
                try:
                    original = _decode_quoted(om.group(1))
                except Exception:
                    i += 1
                    continue

                j = i + 1
                while j < len(lines):
                    candidate = lines[j].rstrip("\r\n")
                    if _TRANSLATE.match(candidate) or _OLD.match(candidate):
                        break

                    nm = _NEW.match(candidate)
                    if nm:
                        try:
                            current = _decode_quoted(nm.group(1))
                        except Exception:
                            break

                        entries.append({
                            "kind": "string",
                            "file": path,
                            "relative": str(path.relative_to(root)),
                            "source_line": i,
                            "target_line": j,
                            "original": original,
                            "current": current,
                            "original_token": om.group(1),
                            "current_token": nm.group(1),
                            "bom": bom,
                        })
                        i = j
                        break
                    j += 1

        elif language and not is_strings:
            stripped = raw.lstrip()
            if stripped.startswith("#") and not stripped.startswith("# game/"):
                comment = stripped[1:].lstrip()
                original_info = _extract_last_string(comment)

                if original_info:
                    original = original_info[0]
                    j = i + 1

                    while j < len(lines):
                        candidate = lines[j].rstrip("\r\n")
                        if _TRANSLATE.match(candidate):
                            break

                        cstrip = candidate.lstrip()
                        if not candidate.strip() or cstrip.startswith("voice "):
                            j += 1
                            continue
                        if cstrip.startswith("#"):
                            break

                        target_info = _extract_last_string(candidate)
                        if target_info:
                            source_match = list(_QUOTED.finditer(comment))
                            target_match = list(_QUOTED.finditer(candidate))
                            entries.append({
                                "kind": "dialogue",
                                "file": path,
                                "relative": str(path.relative_to(root)),
                                "source_line": i,
                                "target_line": j,
                                "original": original,
                                "current": target_info[0],
                                "original_token": source_match[-1].group(0),
                                "current_token": target_match[-1].group(0),
                                "bom": bom,
                            })
                        break
        i += 1

    return entries


def scan_tl(tl_dir, progress=None):
    root = Path(tl_dir).resolve()
    paths = list_rpy(root)
    entries = []
    total = max(1, len(paths))

    for index, path in enumerate(paths, 1):
        entries.extend(scan_file(path, root))
        # Scanner ocupa aproximadamente os primeiros 70% da operação.
        _notify(progress, 70.0 * index / total, f"Lendo arquivos: {index}/{len(paths)}")

    return root, entries


# ---------------- TXT ----------------

def _write_txt_records(path: Path, values):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for value in values:
            f.write(value + "\n")


def _read_txt_records(path: Path):
    return path.read_text(encoding="utf-8-sig").splitlines()


def _clean_txt_outputs(output_dir: Path):
    for name in (FULL_OLD_TXT, FULL_NEW_TXT):
        p = output_dir / name
        if p.exists():
            p.unlink()
    for p in output_dir.glob("old_*.txt"):
        p.unlink()
    for p in output_dir.glob("new_*.txt"):
        p.unlink()


def export_full(tl_dir, output_dir, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    root, entries = scan_tl(tl_dir, progress=progress)
    _clean_txt_outputs(output_dir)

    _notify(progress, 82, "Gravando old.txt...")
    _write_txt_records(output_dir / FULL_OLD_TXT, [e["original_token"] for e in entries])
    _notify(progress, 94, "Gravando new.txt...")
    _write_txt_records(output_dir / FULL_NEW_TXT, [e["current_token"] for e in entries])
    _notify(progress, 100, "TXT completo concluído.")

    session = {"root": root, "entries": entries, "format": "txt"}
    if return_session:
        return output_dir, len(entries), session
    return output_dir, len(entries)


def export_blocks(tl_dir, output_dir, max_bytes=200 * 1024, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    root, entries = scan_tl(tl_dir, progress=progress)
    _clean_txt_outputs(output_dir)

    blocks = []
    current = []
    current_bytes = 0

    for entry in entries:
        size = len((entry["original_token"] + "\n").encode("utf-8"))
        if current and current_bytes + size > max_bytes:
            blocks.append(current)
            current = []
            current_bytes = 0
        current.append(entry)
        current_bytes += size
    if current:
        blocks.append(current)

    total_blocks = max(1, len(blocks))
    for idx, block in enumerate(blocks, 1):
        _write_txt_records(output_dir / f"old_{idx}.txt", [e["original_token"] for e in block])
        _write_txt_records(output_dir / f"new_{idx}.txt", [e["current_token"] for e in block])
        _notify(progress, 70 + 30 * idx / total_blocks, f"Gravando blocos TXT: {idx}/{len(blocks)}")

    session = {"root": root, "entries": entries, "format": "txt"}
    if return_session:
        return output_dir, len(entries), len(blocks), session
    return output_dir, len(entries), len(blocks)


def _block_number(path: Path):
    try:
        return int(path.stem.rsplit("_", 1)[1])
    except Exception:
        return 10**12


def _collect_txt_pair(output_dir: Path):
    full_old = output_dir / FULL_OLD_TXT
    full_new = output_dir / FULL_NEW_TXT

    if full_old.exists() or full_new.exists():
        if not full_old.exists() or not full_new.exists():
            raise FileNotFoundError("É necessário ter old.txt e new.txt juntos.")
        old_records = _read_txt_records(full_old)
        new_records = _read_txt_records(full_new)
        sources = [(full_new.name, i, "linha") for i in range(1, len(new_records) + 1)]
        return old_records, new_records, "TXT completo", sources

    old_blocks = sorted(output_dir.glob("old_*.txt"), key=_block_number)
    new_blocks = sorted(output_dir.glob("new_*.txt"), key=_block_number)

    if not old_blocks and not new_blocks:
        raise FileNotFoundError("Não encontrei old.txt/new.txt nem blocos TXT numerados ao lado do programa.")
    if len(old_blocks) != len(new_blocks):
        raise ValueError(
            f"Quantidade de blocos TXT OLD/NEW diferente: {len(old_blocks)} OLD e {len(new_blocks)} NEW."
        )

    old_records, new_records, sources = [], [], []
    for old_path, new_path in zip(old_blocks, new_blocks):
        if _block_number(old_path) != _block_number(new_path):
            raise ValueError(f"Blocos TXT sem par correspondente: {old_path.name} / {new_path.name}")
        old_part = _read_txt_records(old_path)
        new_part = _read_txt_records(new_path)
        old_records.extend(old_part)
        new_records.extend(new_part)
        sources.extend((new_path.name, i, "linha") for i in range(1, len(new_part) + 1))

    return old_records, new_records, "TXT em blocos", sources


# ---------------- DOCX ----------------

def _clean_docx_outputs(output_dir: Path):
    for name in (FULL_OLD_DOCX, FULL_NEW_DOCX):
        p = output_dir / name
        if p.exists():
            p.unlink()
    for p in output_dir.glob("old_*.docx"):
        p.unlink()
    for p in output_dir.glob("new_*.docx"):
        p.unlink()


def _xml_safe_text(value):
    # XML 1.0 não aceita alguns caracteres de controle.
    value = str(value)
    return "".join(
        ch for ch in value
        if ch in "\t\n\r" or ord(ch) >= 0x20
    )


def _make_docx_bytes(values) -> bytes:
    """
    Cria o DOCX em lote.
    A versão anterior chamava document.add_paragraph() dezenas de milhares
    de vezes; isso ficava muito pesado em PCs modestos.
    Aqui usamos python-docx apenas para criar o pacote-base e montamos
    document.xml de uma vez.
    """
    template = Document()
    template_stream = io.BytesIO()
    template.save(template_stream)

    paragraphs = []
    append = paragraphs.append
    for value in values:
        text = escape(_xml_safe_text(value))
        append(
            '<w:p><w:r><w:t xml:space="preserve">'
            + text +
            '</w:t></w:r></w:p>'
        )

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        + "".join(paragraphs) +
        '<w:sectPr>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/>'
        '</w:sectPr>'
        '</w:body></w:document>'
    ).encode("utf-8")

    out = io.BytesIO()
    template_stream.seek(0)
    with zipfile.ZipFile(template_stream, "r") as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(item, document_xml)
            else:
                zout.writestr(item, zin.read(item.filename))
    return out.getvalue()


def _write_docx_records(path: Path, values):
    path.write_bytes(_make_docx_bytes(values))


def _read_docx_records(path: Path):
    """
    Leitura direta do XML para arquivos grandes.
    Junta todos os runs de cada parágrafo, inclusive documentos que
    tradutores online tenham dividido em vários runs.
    """
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path, "r") as z:
        xml_data = z.read("word/document.xml")

    root = ET.fromstring(xml_data)
    records = []
    for paragraph in root.iter(ns + "p"):
        parts = []
        for node in paragraph.iter():
            if node.tag == ns + "t" and node.text:
                parts.append(node.text)
            elif node.tag == ns + "tab":
                parts.append("\t")
            elif node.tag in (ns + "br", ns + "cr"):
                parts.append("\n")
        records.append("".join(parts))
    return records


def export_full_docx(tl_dir, output_dir, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    root, entries = scan_tl(tl_dir, progress=progress)
    _clean_docx_outputs(output_dir)

    _notify(progress, 80, "Criando old.docx...")
    _write_docx_records(output_dir / FULL_OLD_DOCX, [e["original_token"] for e in entries])
    _notify(progress, 94, "Criando new.docx...")
    _write_docx_records(output_dir / FULL_NEW_DOCX, [e["current_token"] for e in entries])
    _notify(progress, 100, "DOCX completo concluído.")

    session = {"root": root, "entries": entries, "format": "docx"}
    if return_session:
        return output_dir, len(entries), session
    return output_dir, len(entries)


def _fit_docx_blocks(entries, max_file_bytes, progress=None):
    """
    Divide em blocos de forma conservadora e depois mede o DOCX real.
    O alvo fica abaixo de 200 KB para deixar margem ao serviço online.
    """
    # Pré-divisão barata por bytes de texto para evitar remontar DOCX a cada registro.
    approx_limit = 240 * 1024
    rough = []
    current = []
    current_bytes = 0

    for entry in entries:
        # OLD e NEW entram no cálculo para que ambos os arquivos gerados caibam.
        size = max(
            len((entry["original_token"] + "\n").encode("utf-8")),
            len((entry["current_token"] + "\n").encode("utf-8")),
        )
        if current and current_bytes + size > approx_limit:
            rough.append(current)
            current = []
            current_bytes = 0
        current.append(entry)
        current_bytes += size
    if current:
        rough.append(current)

    fitted = []

    def split_until_fit(block):
        old_bytes = _make_docx_bytes([e["original_token"] for e in block])
        new_bytes = _make_docx_bytes([e["current_token"] for e in block])
        if max(len(old_bytes), len(new_bytes)) <= max_file_bytes or len(block) <= 1:
            fitted.append((block, old_bytes, new_bytes))
            return
        mid = len(block) // 2
        split_until_fit(block[:mid])
        split_until_fit(block[mid:])

    for idx, block in enumerate(rough, 1):
        split_until_fit(block)
        _notify(progress, 72 + 10 * idx / max(1, len(rough)), f"Preparando blocos DOCX: {idx}/{len(rough)}")

    return fitted


def export_blocks_docx(
    tl_dir,
    output_dir,
    max_file_bytes=190 * 1024,
    return_session=False,
    progress=None,
):
    output_dir = Path(output_dir).resolve()
    root, entries = scan_tl(tl_dir, progress=progress)
    _clean_docx_outputs(output_dir)

    fitted = _fit_docx_blocks(entries, max_file_bytes=max_file_bytes, progress=progress)
    total = max(1, len(fitted))

    for idx, (block, old_bytes, new_bytes) in enumerate(fitted, 1):
        (output_dir / f"old_{idx}.docx").write_bytes(old_bytes)
        (output_dir / f"new_{idx}.docx").write_bytes(new_bytes)
        _notify(progress, 82 + 18 * idx / total, f"Gravando blocos DOCX: {idx}/{len(fitted)}")

    session = {"root": root, "entries": entries, "format": "docx"}
    if return_session:
        return output_dir, len(entries), len(fitted), session
    return output_dir, len(entries), len(fitted)


def _collect_docx_pair(output_dir: Path):
    full_old = output_dir / FULL_OLD_DOCX
    full_new = output_dir / FULL_NEW_DOCX

    if full_old.exists() or full_new.exists():
        if not full_old.exists() or not full_new.exists():
            raise FileNotFoundError("É necessário ter old.docx e new.docx juntos.")
        old_records = _read_docx_records(full_old)
        new_records = _read_docx_records(full_new)
        sources = [(full_new.name, i, "parágrafo") for i in range(1, len(new_records) + 1)]
        return old_records, new_records, "DOCX completo", sources

    old_blocks = sorted(output_dir.glob("old_*.docx"), key=_block_number)
    new_blocks = sorted(output_dir.glob("new_*.docx"), key=_block_number)

    if not old_blocks and not new_blocks:
        raise FileNotFoundError("Não encontrei old.docx/new.docx nem blocos DOCX numerados ao lado do programa.")
    if len(old_blocks) != len(new_blocks):
        raise ValueError(
            f"Quantidade de blocos DOCX OLD/NEW diferente: {len(old_blocks)} OLD e {len(new_blocks)} NEW."
        )

    old_records, new_records, sources = [], [], []
    for old_path, new_path in zip(old_blocks, new_blocks):
        if _block_number(old_path) != _block_number(new_path):
            raise ValueError(f"Blocos DOCX sem par correspondente: {old_path.name} / {new_path.name}")
        old_part = _read_docx_records(old_path)
        new_part = _read_docx_records(new_path)
        old_records.extend(old_part)
        new_records.extend(new_part)
        sources.extend((new_path.name, i, "parágrafo") for i in range(1, len(new_part) + 1))

    return old_records, new_records, "DOCX em blocos", sources


# ---------------- INJEÇÃO COMUM ----------------

def _validate_token(token: str, record_number: int, label="arquivo") -> str:
    token = token.strip()
    if not token:
        raise ValueError(
            f"O registro {record_number} do {label} está vazio. "
            'Ele deve manter as aspas, por exemplo: "".'
        )
    try:
        return _decode_quoted(token)
    except Exception as exc:
        raise ValueError(
            f"Registro {record_number} inválido no {label}: {token!r}. "
            'Mantenha cada tradução entre aspas duplas.'
        ) from exc


def _inject_common(tl_dir, output_dir, collector, session=None, progress=None):
    output_dir = Path(output_dir).resolve()
    root = Path(tl_dir).resolve()

    _notify(progress, 2, "Preparando injeção...")
    if session is not None and Path(session.get("root", "")).resolve() == root:
        entries = session["entries"]
        _notify(progress, 15, "Usando mapa da extração atual...")
    else:
        # Se o programa foi reaberto, reconstrói o mapa com segurança.
        root, entries = scan_tl(root, progress=lambda v, t=None: _notify(progress, 5 + v * 0.45, t))

    old_records, new_records, mode, sources = collector(output_dir)
    _notify(progress, 55, "Validando OLD/NEW...")

    expected = len(entries)
    if len(old_records) != expected:
        raise ValueError(
            f"O OLD possui {len(old_records)} registros, mas a pasta TL possui {expected} registros traduzíveis. Nada foi alterado."
        )
    if len(new_records) != expected:
        raise ValueError(
            f"O NEW possui {len(new_records)} registros, mas são esperados {expected}. Nada foi alterado."
        )

    for idx, (entry, old_line) in enumerate(zip(entries, old_records), 1):
        if old_line != entry["original_token"]:
            raise ValueError(
                f"O OLD não corresponde à pasta TL no registro {idx}. "
                "Selecione a mesma pasta usada na extração ou faça uma nova extração. Nada foi alterado."
            )
        if idx % 500 == 0 or idx == expected:
            _notify(progress, 55 + 10 * idx / max(1, expected), f"Validando: {idx}/{expected}")

    per_file = {}
    for idx, (entry, new_line) in enumerate(zip(entries, new_records), 1):
        source_name, local_number, unit = sources[idx - 1]
        label = f"{source_name} ({unit} {local_number}; registro global {idx})"
        translated = _validate_token(new_line, idx, label=label)
        per_file.setdefault(entry["file"], []).append((entry, translated))

    prepared = {}
    files = list(per_file.items())
    for file_index, (path, replacements) in enumerate(files, 1):
        text, bom = _read_text(path)
        lines = text.splitlines(keepends=True)

        for entry, translated in replacements:
            line_index = entry["target_line"]
            if line_index < 0 or line_index >= len(lines):
                raise ValueError(
                    f"A estrutura mudou em {entry['relative']} perto da linha {line_index + 1}. Nada foi alterado."
                )

            ending = "\r\n" if lines[line_index].endswith("\r\n") else (
                "\n" if lines[line_index].endswith("\n") else ""
            )
            body = lines[line_index][:-len(ending)] if ending else lines[line_index]
            if not _extract_last_string(body):
                raise ValueError(
                    f"Destino inválido em {entry['relative']}:{line_index + 1}. Nada foi alterado."
                )
            lines[line_index] = _replace_last_string(body, translated) + ending

        prepared[path] = ("".join(lines), bom)
        _notify(progress, 65 + 25 * file_index / max(1, len(files)), f"Preparando arquivos: {file_index}/{len(files)}")

    # Só grava depois de tudo validado e preparado.
    for file_index, (path, (text, bom)) in enumerate(prepared.items(), 1):
        _write_text(path, text, bom)
        _notify(progress, 90 + 10 * file_index / max(1, len(prepared)), f"Gravando arquivos: {file_index}/{len(prepared)}")

    _notify(progress, 100, "Injeção concluída.")
    return expected, mode


def inject_translations(tl_dir, output_dir, session=None, progress=None):
    return _inject_common(tl_dir, output_dir, _collect_txt_pair, session=session, progress=progress)


def inject_docx_translations(tl_dir, output_dir, session=None, progress=None):
    return _inject_common(tl_dir, output_dir, _collect_docx_pair, session=session, progress=progress)
