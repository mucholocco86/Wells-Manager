# -*- coding: utf-8 -*-
"""
Wells JSON - extração/reinjeção de traduções automáticas.

Fluxo separado do TL/RPY tradicional:
JSON (chave nativa -> valor traduzido) -> nativo/traduzido TXT ou DOCX ->
revisão externa -> reinjeção somente dos valores.

As chaves nativas são a âncora estrutural e nunca são alteradas.
"""
from __future__ import annotations

import ast
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

from docx import Document


FULL_NATIVE_TXT = "nativo.txt"
FULL_TRANSLATED_TXT = "traduzido.txt"
FULL_NATIVE_DOCX = "nativo.docx"
FULL_TRANSLATED_DOCX = "traduzido.docx"


def _notify(progress, value, text=None):
    if progress:
        progress(max(0.0, min(100.0, float(value))), text)


def _load_json(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    try:
        # Lista de pares em vez de dict: alguns JSONs reais possuem a mesma
        # chave mais de uma vez. Um dict Python apagaria silenciosamente as
        # ocorrências anteriores. Aqui preservamos cada registro e sua ordem.
        data = json.loads(text, object_pairs_hook=lambda pairs: pairs)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("O JSON precisa ser um objeto no formato texto nativo -> tradução.")
    for item in data:
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            raise ValueError("O JSON contém uma estrutura interna não suportada.")
        key, value = item
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("O JSON contém entradas que não são pares de texto -> texto.")

    # Detecta o estilo dos exemplos sem transformar isso em requisito.
    indent = 4 if "\n    \"" in text[:10000] else 2
    newline = "\r\n" if "\r\n" in text else "\n"
    final_newline = text.endswith(("\n", "\r"))
    return path, data, {
        "bom": bom,
        "indent": indent,
        "newline": newline,
        "final_newline": final_newline,
    }


def _encode_record(value):
    # Um registro por linha/parágrafo. json.dumps mantém \n, aspas e barras
    # escapados, evitando quebrar o alinhamento nativo/traduzido.
    return json.dumps(value, ensure_ascii=False)


def _decode_record(token, number, label):
    token = str(token).strip()
    if not token:
        raise ValueError(f"Registro {number} vazio em {label}.")
    try:
        value = json.loads(token)
    except Exception:
        # Compatibilidade conservadora com documentos que mantenham a mesma
        # sintaxe de string mas tenham sido lidos por ferramentas Python.
        try:
            value = ast.literal_eval(token)
        except Exception as exc:
            raise ValueError(
                f"Registro {number} inválido em {label}. "
                "Mantenha cada entrada como uma string entre aspas."
            ) from exc
    if not isinstance(value, str):
        raise ValueError(f"Registro {number} de {label} não é texto.")
    return value


def _records(data):
    return [
        {"native": key, "translated": value}
        for key, value in data
    ]


# ---------------- TXT ----------------

def _write_txt(path, values):
    with Path(path).open("w", encoding="utf-8", newline="\n") as f:
        for value in values:
            f.write(_encode_record(value) + "\n")


def _read_txt(path):
    return Path(path).read_text(encoding="utf-8-sig").splitlines()


def _clean_txt(output_dir):
    for name in (FULL_NATIVE_TXT, FULL_TRANSLATED_TXT):
        p = output_dir / name
        if p.exists():
            p.unlink()
    for pattern in ("nativo_*.txt", "traduzido_*.txt"):
        for p in output_dir.glob(pattern):
            p.unlink()


def export_json_full_txt(json_path, output_dir, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source, data, style = _load_json(json_path)
    entries = _records(data)
    _clean_txt(output_dir)

    _notify(progress, 35, "Gravando nativo.txt...")
    _write_txt(output_dir / FULL_NATIVE_TXT, [e["native"] for e in entries])
    _notify(progress, 75, "Gravando traduzido.txt...")
    _write_txt(output_dir / FULL_TRANSLATED_TXT, [e["translated"] for e in entries])
    _notify(progress, 100, "JSON → TXT concluído.")

    session = {"json": source, "keys": [e["native"] for e in entries], "style": style, "format": "txt"}
    result = (output_dir, len(entries), session)
    return result if return_session else result[:2]


def _split_txt(entries, max_bytes):
    blocks, current = [], []
    native_bytes = translated_bytes = 0
    for entry in entries:
        nsize = len((_encode_record(entry["native"]) + "\n").encode("utf-8"))
        tsize = len((_encode_record(entry["translated"]) + "\n").encode("utf-8"))
        if current and (native_bytes + nsize > max_bytes or translated_bytes + tsize > max_bytes):
            blocks.append(current)
            current = []
            native_bytes = translated_bytes = 0
        current.append(entry)
        native_bytes += nsize
        translated_bytes += tsize
    if current:
        blocks.append(current)
    return blocks


def export_json_blocks_txt(json_path, output_dir, max_bytes=200 * 1024, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source, data, style = _load_json(json_path)
    entries = _records(data)
    _clean_txt(output_dir)
    blocks = _split_txt(entries, max_bytes)

    total = max(1, len(blocks))
    for idx, block in enumerate(blocks, 1):
        _write_txt(output_dir / f"nativo_{idx}.txt", [e["native"] for e in block])
        _write_txt(output_dir / f"traduzido_{idx}.txt", [e["translated"] for e in block])
        _notify(progress, 100 * idx / total, f"Gravando blocos TXT: {idx}/{len(blocks)}")

    session = {"json": source, "keys": [e["native"] for e in entries], "style": style, "format": "txt"}
    result = (output_dir, len(entries), len(blocks), session)
    return result if return_session else result[:3]


# ---------------- DOCX ----------------

def _xml_safe(value):
    return "".join(ch for ch in str(value) if ch in "\t\n\r" or ord(ch) >= 0x20)


def _make_docx(values):
    template = Document()
    stream = io.BytesIO()
    template.save(stream)

    paragraphs = []
    for value in values:
        text = escape(_xml_safe(_encode_record(value)))
        paragraphs.append('<w:p><w:r><w:t xml:space="preserve">' + text + '</w:t></w:r></w:p>')

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + "".join(paragraphs) +
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
        '</w:body></w:document>'
    ).encode("utf-8")

    out = io.BytesIO()
    stream.seek(0)
    with zipfile.ZipFile(stream, "r") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            zout.writestr(item, document_xml if item.filename == "word/document.xml" else zin.read(item.filename))
    return out.getvalue()


def _write_docx(path, values):
    Path(path).write_bytes(_make_docx(values))


def _read_docx(path):
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path, "r") as z:
        root = ET.fromstring(z.read("word/document.xml"))
    records = []
    for p in root.iter(ns + "p"):
        parts = []
        for node in p.iter():
            if node.tag == ns + "t" and node.text:
                parts.append(node.text)
            elif node.tag == ns + "tab":
                parts.append("\t")
            elif node.tag in (ns + "br", ns + "cr"):
                parts.append("\n")
        records.append("".join(parts))
    return records


def _clean_docx(output_dir):
    for name in (FULL_NATIVE_DOCX, FULL_TRANSLATED_DOCX):
        p = output_dir / name
        if p.exists():
            p.unlink()
    for pattern in ("nativo_*.docx", "traduzido_*.docx"):
        for p in output_dir.glob(pattern):
            p.unlink()


def export_json_full_docx(json_path, output_dir, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source, data, style = _load_json(json_path)
    entries = _records(data)
    _clean_docx(output_dir)

    _notify(progress, 25, "Criando nativo.docx...")
    _write_docx(output_dir / FULL_NATIVE_DOCX, [e["native"] for e in entries])
    _notify(progress, 70, "Criando traduzido.docx...")
    _write_docx(output_dir / FULL_TRANSLATED_DOCX, [e["translated"] for e in entries])
    _notify(progress, 100, "JSON → DOCX concluído.")

    session = {"json": source, "keys": [e["native"] for e in entries], "style": style, "format": "docx"}
    result = (output_dir, len(entries), session)
    return result if return_session else result[:2]


def _fit_docx_blocks(entries, max_file_bytes, progress=None):
    rough = _split_txt(entries, 240 * 1024)
    fitted = []

    def fit(block):
        native = _make_docx([e["native"] for e in block])
        translated = _make_docx([e["translated"] for e in block])
        if max(len(native), len(translated)) <= max_file_bytes or len(block) <= 1:
            fitted.append((block, native, translated))
            return
        mid = len(block) // 2
        fit(block[:mid])
        fit(block[mid:])

    for idx, block in enumerate(rough, 1):
        fit(block)
        _notify(progress, 60 * idx / max(1, len(rough)), f"Preparando blocos DOCX: {idx}/{len(rough)}")
    return fitted


def export_json_blocks_docx(json_path, output_dir, max_file_bytes=190 * 1024, return_session=False, progress=None):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source, data, style = _load_json(json_path)
    entries = _records(data)
    _clean_docx(output_dir)
    fitted = _fit_docx_blocks(entries, max_file_bytes, progress)

    total = max(1, len(fitted))
    for idx, (block, native_bytes, translated_bytes) in enumerate(fitted, 1):
        (output_dir / f"nativo_{idx}.docx").write_bytes(native_bytes)
        (output_dir / f"traduzido_{idx}.docx").write_bytes(translated_bytes)
        _notify(progress, 60 + 40 * idx / total, f"Gravando blocos DOCX: {idx}/{len(fitted)}")

    session = {"json": source, "keys": [e["native"] for e in entries], "style": style, "format": "docx"}
    result = (output_dir, len(entries), len(fitted), session)
    return result if return_session else result[:3]


# ---------------- COLETA / REINJEÇÃO ----------------

def _block_number(path):
    try:
        return int(Path(path).stem.rsplit("_", 1)[1])
    except Exception:
        return 10**12


def _collect_pair(output_dir, fmt):
    output_dir = Path(output_dir)
    if fmt == "txt":
        reader = _read_txt
        full_n, full_t = output_dir / FULL_NATIVE_TXT, output_dir / FULL_TRANSLATED_TXT
        pattern_n, pattern_t = "nativo_*.txt", "traduzido_*.txt"
        mode_full, mode_blocks = "JSON/TXT completo", "JSON/TXT em blocos"
    elif fmt == "docx":
        reader = _read_docx
        full_n, full_t = output_dir / FULL_NATIVE_DOCX, output_dir / FULL_TRANSLATED_DOCX
        pattern_n, pattern_t = "nativo_*.docx", "traduzido_*.docx"
        mode_full, mode_blocks = "JSON/DOCX completo", "JSON/DOCX em blocos"
    else:
        raise ValueError("Formato JSON desconhecido.")

    if full_n.exists() or full_t.exists():
        if not (full_n.exists() and full_t.exists()):
            raise FileNotFoundError("Os arquivos nativo e traduzido precisam existir juntos.")
        return reader(full_n), reader(full_t), mode_full

    natives = sorted(output_dir.glob(pattern_n), key=_block_number)
    translated = sorted(output_dir.glob(pattern_t), key=_block_number)
    if not natives and not translated:
        raise FileNotFoundError("Não encontrei os arquivos nativo/traduzido desta extração JSON.")
    if len(natives) != len(translated):
        raise ValueError("Quantidade de blocos nativo/traduzido diferente.")

    nrecords, trecords = [], []
    for np, tp in zip(natives, translated):
        if _block_number(np) != _block_number(tp):
            raise ValueError(f"Blocos sem par correspondente: {np.name} / {tp.name}")
        nr, tr = reader(np), reader(tp)
        if len(nr) != len(tr):
            raise ValueError(f"Bloco desalinhado: {np.name} tem {len(nr)} registros e {tp.name} tem {len(tr)}.")
        nrecords.extend(nr)
        trecords.extend(tr)
    return nrecords, trecords, mode_blocks


def _serialize_json(data, style):
    # Serialização manual do objeto para preservar inclusive chaves repetidas,
    # algo que json.dumps(dict) não consegue representar.
    indent = " " * int(style.get("indent", 2))
    lines = ["{"]
    total = len(data)
    for idx, (key, value) in enumerate(data, 1):
        comma = "," if idx < total else ""
        lines.append(
            indent
            + json.dumps(key, ensure_ascii=False)
            + ": "
            + json.dumps(value, ensure_ascii=False)
            + comma
        )
    lines.append("}")
    newline = style.get("newline", "\n")
    text = newline.join(lines)
    if style.get("final_newline", True):
        text += newline
    raw = text.encode("utf-8")
    if style.get("bom"):
        raw = b"\xef\xbb\xbf" + raw
    return raw


def inject_json_translations(json_path, output_dir, fmt, session=None, progress=None):
    source, data, detected_style = _load_json(json_path)
    _notify(progress, 10, "Validando pares nativo/traduzido...")
    native_records, translated_records, mode = _collect_pair(Path(output_dir), fmt)

    if len(native_records) != len(translated_records):
        raise ValueError(
            f"Quantidade de registros diferente: {len(native_records)} nativos e "
            f"{len(translated_records)} traduzidos."
        )

    natives = [_decode_record(v, i, "nativo") for i, v in enumerate(native_records, 1)]
    translated = [_decode_record(v, i, "traduzido") for i, v in enumerate(translated_records, 1)]

    if session is not None:
        session_path = Path(session.get("json", "")).resolve()
        if session_path != source:
            raise ValueError("O JSON selecionado não é o mesmo usado nesta extração.")
        expected = list(session.get("keys", []))
        if natives != expected:
            raise ValueError(
                "O arquivo nativo foi alterado ou não pertence a esta extração. "
                "A reinjeção foi cancelada para evitar deslocamento de traduções."
            )

    json_keys = [key for key, _ in data]
    if len(natives) != len(data):
        raise ValueError(
            f"O documento possui {len(natives)} entradas, mas o JSON possui {len(data)}. "
            "A reinjeção foi cancelada."
        )

    # A ordem também é parte da âncora. Isso permite trabalhar com JSONs reais
    # que possuem chaves repetidas sem confundir uma ocorrência com outra.
    if natives != json_keys:
        for idx, (document_key, json_key) in enumerate(zip(natives, json_keys), 1):
            if document_key != json_key:
                raise ValueError(
                    f"O nativo diverge do JSON no registro {idx}: "
                    f"{document_key!r} != {json_key!r}. Reinjeção cancelada."
                )
        raise ValueError("As chaves do documento nativo não correspondem exatamente ao JSON.")

    # Atualiza por ocorrência, preservando chave, ordem e duplicatas.
    updated = []
    total = max(1, len(natives))
    for idx, ((json_key, _old_value), native, value) in enumerate(
        zip(data, natives, translated), 1
    ):
        if json_key != native:
            raise ValueError(f"Âncora nativa divergente no registro {idx}.")
        updated.append((json_key, value))
        if idx == 1 or idx % 500 == 0 or idx == len(natives):
            _notify(progress, 15 + 70 * idx / total, f"Preparando reinjeção: {idx}/{len(natives)}")

    style = session.get("style", detected_style) if session else detected_style
    raw = _serialize_json(updated, style)

    # Escrita atômica: o original só é substituído depois de toda validação.
    fd, temp_name = tempfile.mkstemp(prefix=source.name + ".", suffix=".wells_tmp", dir=str(source.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, source)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise

    _notify(progress, 100, "Reinjeção JSON concluída.")
    return len(natives), mode
