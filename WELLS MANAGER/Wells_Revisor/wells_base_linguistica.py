# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import csv, re, unicodedata

WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ]+)*", re.UNICODE)

def _fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.casefold())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

class BaseLinguistica:
    """Consulta lexical/morfológica. Não reescreve frases por conta própria."""
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        d = self.base_dir / "dados_linguisticos"
        self.palavras = self._load_set(d / "Palavras_PT-BR.txt")
        self.lexico = self._load_set(d / "fserb_lexico.txt")
        self.verbos = self._load_set(d / "fserb_verbos.txt")
        self.conjugacoes = self._load_set(d / "fserb_conjugacoes.txt")
        self.icf = self._load_icf(d / "fserb_icf.csv")
        self.vocab = self.palavras | self.lexico | self.conjugacoes
        self.acentos = {}
        for w in self.vocab:
            k = _fold(w)
            if k != w:
                self.acentos.setdefault(k, set()).add(w)

    @staticmethod
    def _load_set(path):
        if not path.is_file(): return set()
        return {x.strip().casefold() for x in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines() if x.strip()}

    @staticmethod
    def _load_icf(path):
        out = {}
        if not path.is_file(): return out
        with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    try: out[row[0].casefold()] = float(row[1])
                    except ValueError: pass
        return out

    def existe(self, palavra):
        return palavra.casefold() in self.vocab

    def e_verbo(self, palavra):
        w = palavra.casefold()
        return w in self.verbos or w in self.conjugacoes

    def restaurar_acento_univoco(self, palavra):
        """Só sugere acento quando há UMA única forma acentuada equivalente."""
        w = palavra.casefold()
        if w in self.vocab:
            return None
        formas = self.acentos.get(_fold(w), set())
        if len(formas) == 1:
            return next(iter(formas))
        return None

    def frequencia_relativa(self, palavra):
        # ICF menor = forma mais comum no corpus.
        return self.icf.get(palavra.casefold())

def preservar_caixa(orig, novo):
    if orig.isupper(): return novo.upper()
    if orig[:1].isupper(): return novo[:1].upper() + novo[1:]
    return novo
