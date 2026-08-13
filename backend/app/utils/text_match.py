"""Similarité textuelle partagée (forum, documents)."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

STOP_WORDS = {
    "les", "des", "une", "dans", "pour", "par", "sur", "avec", "sans", "est", "sont",
    "comment", "quoi", "quel", "quelle", "quels", "quelles", "qui", "que", "qu",
    "peut", "peux", "peuvent", "dois", "doit", "faut", "être", "avoir", "faire",
    "donc", "mais", "car", "donc", "aussi", "très", "plus", "moins", "tout", "tous",
    "cette", "cela", "celui", "celle", "ceux", "celles", "mon", "mes", "ton", "tes",
    "son", "ses", "notre", "nos", "votre", "vos", "leur", "leurs", "the", "and", "or",
}


def tokenize(text: str) -> set[str]:
    raw = re.findall(r"[a-zA-Zàâäéèêëïîôùûüç0-9]{3,}", (text or "").lower())
    return {t for t in raw if t not in STOP_WORDS}


def similarity_score(query: str, candidate: str) -> float:
    """Score 0..1 — seuil recommandé : 0.38 minimum."""
    q = (query or "").strip().lower()
    c = (candidate or "").strip().lower()
    if not q or not c:
        return 0.0

    q_tokens = tokenize(q)
    c_tokens = tokenize(c)
    if not q_tokens:
        return 0.0

    overlap = q_tokens & c_tokens
    if len(overlap) < 2:
        # Autoriser 1 seul token si très long et présent dans le titre
        if len(overlap) == 1:
            only = next(iter(overlap))
            if len(only) < 5:
                return 0.0
        else:
            return 0.0

    token_ratio = len(overlap) / len(q_tokens)
    seq_ratio = SequenceMatcher(None, q, c).ratio()
    score = 0.55 * token_ratio + 0.45 * seq_ratio

    if score < 0.38:
        return 0.0
    return score
