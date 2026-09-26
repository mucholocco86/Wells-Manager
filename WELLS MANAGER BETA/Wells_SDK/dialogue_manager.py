# -*- coding: utf-8 -*-
"""User-facing Wells Manager translation document flow.

The native Ren'Py dialogue TAB is an internal anchor only. The user works with
TXT/DOCX documents carrying simple Wxxxxxxxx serials, while the physical JSON
map retains the Ren'Py source/target metadata needed for safe reinjection.
"""
from __future__ import annotations

import json
from pathlib import Path

import dialogue_roundtrip as bridge

BLOCK_TARGET_BYTES = 180 * 1024


class DialogueManagerError(RuntimeError):
    pass


def map_path(output_dir):
    return Path(output_dir).resolve() / bridge.TEMP_DIR_NAME / bridge.MAP_NAME


def pending(output_dir):
    path = map_path(output_dir)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise DialogueManagerError('Mapa físico Wells inválido: {}'.format(exc))
    return payload


def _chunk(records):
    blocks = []
    current = []
    size = 0
    for serial, text in records:
        item_size = len((serial + '\n' + text + '\n').encode('utf-8'))
        if current and size + item_size > BLOCK_TARGET_BYTES:
            blocks.append(current)
            current = []
            size = 0
        current.append((serial, text))
        size += item_size
    if current:
        blocks.append(current)
    return blocks


def _clean_outputs(output_dir, fmt):
    output_dir = Path(output_dir)
    suffix = '.' + fmt
    for path in output_dir.glob('Wells_Dialogue_*' + suffix):
        if path.is_file():
            path.unlink()


def prepare(project, language, fmt='txt', blocks=False, output_dir=None,
            include_strings=True, log=None, progress=None):
    output_dir = Path(output_dir or project).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = pending(output_dir)
    if existing:
        raise DialogueManagerError(
            'Já existe uma extração Wells aguardando retorno. Finalize-a antes de iniciar outra.')

    result = bridge.prepare(
        project, language, fmt=fmt, output_dir=output_dir,
        include_strings=include_strings, log=log, progress=progress)
    path = map_path(output_dir)
    payload = json.loads(path.read_text(encoding='utf-8'))
    payload['wells_manager_mode'] = 'blocks' if blocks else 'full'

    if not blocks:
        payload['documents'] = [Path(result['document']).name]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        result['documents'] = [result['document']]
        result['blocks'] = 1
        return result

    source = Path(result['document'])
    translated = bridge._parse_document(source, fmt)
    records = []
    for entry in payload.get('entries') or []:
        serial = entry['serial'].upper()
        if serial not in translated:
            raise DialogueManagerError('Registro {} não foi encontrado no documento intermediário.'.format(serial))
        records.append((serial, translated[serial]))

    chunks = _chunk(records)
    _clean_outputs(output_dir, fmt)
    documents = []
    for index, chunk in enumerate(chunks, 1):
        name = 'Wells_Dialogue_{:03d}.{}'.format(index, fmt)
        document = output_dir / name
        if fmt == 'docx':
            bridge._write_docx(document, chunk)
        else:
            bridge._write_txt(document, chunk)
        documents.append(name)
        if progress:
            progress(82 + 17 * index / max(1, len(chunks)),
                     'Gravando blocos {}: {}/{}'.format(fmt.upper(), index, len(chunks)))
    if source.exists():
        source.unlink()

    payload['document'] = None
    payload['documents'] = documents
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if log:
        log('Wells: TAB usado internamente; {} e JSON físico preparados em {} bloco(s).'.format(fmt.upper(), len(documents)))
    return {
        'documents': [str(output_dir / name) for name in documents],
        'map': str(path), 'entries': result['entries'],
        'unmatched': result['unmatched'], 'blocks': len(documents),
    }


def inject(project, output_dir, fmt, blocks=False, log=None, progress=None):
    output_dir = Path(output_dir).expanduser().resolve()
    payload = pending(output_dir)
    if not payload:
        raise DialogueManagerError('Nenhuma extração Wells está aguardando retorno.')
    expected_mode = 'blocks' if blocks else 'full'
    if payload.get('format') != fmt or payload.get('wells_manager_mode', 'full') != expected_mode:
        raise DialogueManagerError(
            'Existe uma extração {} {} pendente. Use o mesmo botão que criou os documentos.'.format(
                str(payload.get('format', '')).upper(),
                'em blocos' if payload.get('wells_manager_mode') == 'blocks' else 'completa'))

    documents = payload.get('documents') or []
    if not documents:
        name = payload.get('document')
        if name:
            documents = [name]
    if not documents:
        raise DialogueManagerError('O mapa Wells não contém documentos associados.')

    paths = [output_dir / name for name in documents]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise DialogueManagerError('Documento traduzido não encontrado: {}'.format(missing[0]))

    if not blocks:
        return bridge.inject(project, paths[0], log=log, progress=progress)

    merged = {}
    for index, path in enumerate(paths, 1):
        part = bridge._parse_document(path, fmt)
        duplicate = set(merged).intersection(part)
        if duplicate:
            raise DialogueManagerError('Serial duplicado entre blocos: {}.'.format(sorted(duplicate)[0]))
        merged.update(part)
        if progress:
            progress(5 + 20 * index / max(1, len(paths)),
                     'Lendo blocos traduzidos: {}/{}'.format(index, len(paths)))

    expected = [entry['serial'].upper() for entry in payload.get('entries') or []]
    records = []
    missing_serials = []
    for serial in expected:
        if serial not in merged:
            missing_serials.append(serial)
        else:
            records.append((serial, merged[serial]))
    extras = [serial for serial in merged if serial not in set(expected)]
    if missing_serials or extras:
        raise DialogueManagerError(
            'Os blocos não correspondem ao mapa. Ausentes: {}; extras: {}. Nada foi alterado.'.format(
                ', '.join(missing_serials[:10]) or '0', ', '.join(extras[:10]) or '0'))

    temp = output_dir / ('Wells_Merged_Input.' + fmt)
    try:
        if fmt == 'docx':
            bridge._write_docx(temp, records)
        else:
            bridge._write_txt(temp, records)
        return bridge.inject(project, temp, log=log, progress=progress)
    finally:
        if temp.exists():
            temp.unlink()
