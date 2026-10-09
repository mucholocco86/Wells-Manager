# -*- coding: utf-8 -*-
"""
Wells Isolador Ren'Py.

Base conceitual: renpy/translation/generation.py::generic_filter.
A função percorre a string e entrega ao revisor SOMENTE runs de texto humano,
mantendo [...] (interpolação/substituição) e {...} (text tags) byte-a-byte.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Segmento:
    tipo: str       # "texto" | "protegido"
    valor: str

def segmentar(s: str):
    """Segmenta seguindo a mesma fronteira estrutural de generic_filter()."""
    segmentos = []
    buf = []

    def flush():
        if buf:
            segmentos.append(Segmento("texto", "".join(buf)))
            buf.clear()

    i = 0
    while i < len(s):
        ch = s[i]
        if ch not in "[{":
            buf.append(ch)
            i += 1
            continue

        flush()
        opener = ch
        closer = "]" if ch == "[" else "}"
        depth = 1
        j = i + 1

        # generic_filter preserva o conteúdo delimitado; aqui fazemos o mesmo.
        while j < len(s) and depth:
            if s[j] == opener:
                depth += 1
            elif s[j] == closer:
                depth -= 1
            j += 1

        if depth:
            # Delimitador incompleto: conservadoramente protege o resto.
            segmentos.append(Segmento("protegido", s[i:]))
            i = len(s)
        else:
            segmentos.append(Segmento("protegido", s[i:j]))
            i = j

    flush()
    return segmentos

def transformar_texto(s: str, func: Callable[[str], str]):
    partes = []
    protegidos_antes = []
    for seg in segmentar(s):
        if seg.tipo == "protegido":
            protegidos_antes.append(seg.valor)
            partes.append(seg.valor)
        else:
            partes.append(func(seg.valor))
    resultado = "".join(partes)

    protegidos_depois = [x.valor for x in segmentar(resultado) if x.tipo == "protegido"]
    if protegidos_depois != protegidos_antes:
        raise ValueError("Estrutura Ren'Py protegida foi alterada.")
    return resultado, len(protegidos_antes)
