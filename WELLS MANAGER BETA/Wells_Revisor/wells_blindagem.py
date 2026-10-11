# -*- coding: utf-8 -*-
"""Persistência local das listas manuais do Wells Revisor.

O arquivo blindagem.txt é deliberadamente simples e legível. Ele fica ao lado
do executável (ou do main.py em desenvolvimento), para permanecer junto do
Wells Manager e poder ser copiado/arquivado manualmente.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

LISTA_BLINDADOS = "NOMES_BLINDADOS"
LISTA_TRADUZIVEIS = "NOMES_TRADUZIVEIS"
_LISTAS = (LISTA_BLINDADOS, LISTA_TRADUZIVEIS)


def _vazio():
    return {LISTA_BLINDADOS: [], LISTA_TRADUZIVEIS: []}


def _normalizar_termo(value):
    value = str(value).strip()
    if not value:
        raise ValueError("O termo não pode ficar vazio.")
    if "\n" in value or "\r" in value:
        raise ValueError("Cada entrada deve ocupar uma única linha.")
    return value


def _validar_lista(kind):
    if kind not in _LISTAS:
        raise ValueError("Lista de blindagem desconhecida.")


def carregar_listas(path):
    path = Path(path)
    data = _vazio()
    if not path.exists():
        return data

    current = None
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().upper()
            current = section if section in _LISTAS else None
            continue
        if current is not None:
            # Preserva a grafia escolhida pelo usuário, mas evita duplicatas
            # equivalentes dentro da mesma lista.
            if not any(x.casefold() == line.casefold() for x in data[current]):
                data[current].append(line)
    return data


def salvar_listas(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _vazio()
    for kind in _LISTAS:
        seen = set()
        for value in data.get(kind, []):
            term = _normalizar_termo(value)
            key = term.casefold()
            if key not in seen:
                normalized[kind].append(term)
                seen.add(key)

    text = (
        "# Wells Manager - listas manuais do Revisor\n"
        "# Edite preferencialmente pela interface do programa.\n\n"
        f"[{LISTA_BLINDADOS}]\n"
        + "\n".join(normalized[LISTA_BLINDADOS])
        + "\n\n"
        f"[{LISTA_TRADUZIVEIS}]\n"
        + "\n".join(normalized[LISTA_TRADUZIVEIS])
        + "\n"
    )

    # Gravação atômica para não deixar arquivo parcial se houver interrupção.
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def adicionar_termo(path, kind, value):
    _validar_lista(kind)
    term = _normalizar_termo(value)
    data = carregar_listas(path)
    if any(x.casefold() == term.casefold() for x in data[kind]):
        raise ValueError("Esse termo já existe nesta lista.")
    data[kind].append(term)
    salvar_listas(path, data)
    return term


def editar_termo(path, kind, old_value, new_value):
    _validar_lista(kind)
    old_key = _normalizar_termo(old_value).casefold()
    new_term = _normalizar_termo(new_value)
    data = carregar_listas(path)

    index = next(
        (i for i, value in enumerate(data[kind]) if value.casefold() == old_key),
        None,
    )
    if index is None:
        raise ValueError("A entrada selecionada não existe mais na lista.")
    if any(
        i != index and value.casefold() == new_term.casefold()
        for i, value in enumerate(data[kind])
    ):
        raise ValueError("Esse termo já existe nesta lista.")

    data[kind][index] = new_term
    salvar_listas(path, data)
    return new_term


def excluir_termo(path, kind, value):
    _validar_lista(kind)
    key = _normalizar_termo(value).casefold()
    data = carregar_listas(path)
    index = next(
        (i for i, item in enumerate(data[kind]) if item.casefold() == key),
        None,
    )
    if index is None:
        raise ValueError("A entrada selecionada não existe mais na lista.")
    removed = data[kind].pop(index)
    salvar_listas(path, data)
    return removed


def conflitos(data):
    blindados = {x.casefold(): x for x in data.get(LISTA_BLINDADOS, [])}
    traduziveis = {x.casefold(): x for x in data.get(LISTA_TRADUZIVEIS, [])}
    return [blindados[key] for key in blindados.keys() & traduziveis.keys()]
