# -*- coding: utf-8 -*-
"""
Wells Guia Linguístico PT-BR
Camada conservadora de validação estrutural.

Princípio: corrigir a forma linguística sem censurar, moralizar,
suavizar ou alterar deliberadamente o significado/voz do diálogo.
"""
from __future__ import annotations
import re
from difflib import SequenceMatcher

SPECIAL = re.compile(r'(\[[^\[\]\n]+\]|\{[^{}\n]+\}|%\([^)]+\)[#0\- +]?[0-9.]*[a-zA-Z]|<[^<>\n]+>)')
WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ]+)*")

# Anomalias que o próprio revisor não pode INTRODUZIR.
# Não são filtros de conteúdo; são somente estruturas linguísticas/mecânicas.
INVALIDOS = (
    (re.compile(r"\bque\s+que\b", re.I), "duplicação 'que que'"),
    (re.compile(r"\bdesde\s+que\s+que\b", re.I), "duplicação após 'desde que'"),
    (re.compile(r"__WELLS_", re.I), "marcador interno não restaurado"),
)

def _tokens(text):
    return SPECIAL.findall(text)

def _count(rx, text):
    return len(rx.findall(text))


# Mudanças morfológicas potencialmente semânticas. Sem análise sintática segura,
# o revisor NÃO troca automaticamente masculino/feminino ou singular/plural.
_MORPH_END = re.compile(r"(?i)(?:o|a|os|as)$")

def _palavras(text):
    return WORD.findall(SPECIAL.sub(" ", text))

def _mudanca_morfologica_suspeita(original, revisado):
    a, b = _palavras(original), _palavras(revisado)
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x.casefold() == y.casefold():
            continue
        # Mesmo radical + troca simples o/a/os/as = risco de gênero/número.
        sx, sy = x.casefold(), y.casefold()
        rx = _MORPH_END.sub("", sx)
        ry = _MORPH_END.sub("", sy)
        if rx and rx == ry and _MORPH_END.search(sx) and _MORPH_END.search(sy):
            return True
    return False

def validar_revisao(original: str, revisado: str):
    if original == revisado:
        return True, "sem alteração"

    # Tags/variáveis devem ser exatamente as mesmas e na mesma ordem.
    if _tokens(original) != _tokens(revisado):
        return False, "tag/variável alterada"

    # Não inventa gênero/número por regra local.
    if _mudanca_morfologica_suspeita(original, revisado):
        return False, "mudança de gênero/número sem contexto seguro"

    # Uma anomalia preexistente não autoriza criar outra; rejeita apenas aumento.
    for rx, nome in INVALIDOS:
        if _count(rx, revisado) > _count(rx, original):
            return False, nome

    # Evita reescritas grandes. O Wells é revisor, não autor.
    # Mudanças curtas de sintaxe/pontuação passam; reconstruções extensas não.
    ratio = SequenceMatcher(None, original, revisado).ratio()
    delta = abs(len(revisado) - len(original))
    if len(original) >= 40 and ratio < 0.72 and delta > 12:
        return False, "alteração semântica extensa"

    return True, "aprovado"

def analisar_registro(idx: int, original: str, revisado: str, tokens: int):
    palavras = WORD.findall(original)
    return {
        "id": idx,
        "original": original,
        "revisado": revisado,
        "alterado": original != revisado,
        "tokens_protegidos": tokens,
        "palavras": len(palavras),
    }
