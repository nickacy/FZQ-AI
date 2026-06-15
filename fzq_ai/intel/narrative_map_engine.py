# fzq_ai/intel/narrative_map_engine.py

from __future__ import annotations

from typing import Dict, List
import re
from collections import Counter

def _tokenize(text: str) -> List[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z]+", text)
    return tokens

def _distance(t1: List[str], t2: List[str]) -> float:
    """
    """
    if not t1 or not t2:
        return 1.0

    intersection = sum(min(c1[w], c2[w]) for w in c1.keys() & c2.keys())
    total = sum(c1.values()) + sum(c2.values())

    return float(1 - sim)

class NarrativeMapEngine:
    """
    """

    def compute_distance_matrix(self, narratives: List) -> Dict[str, Dict[str, float]]:
        bloc_texts: Dict[str, List[str]] = {}

        for n in narratives:
            for bloc, text in n.narratives.items():
                bloc_texts.setdefault(bloc, []).append(text)

        bloc_corpus = {bloc: "\n".join(texts) for bloc, texts in bloc_texts.items()}

        tokens = {b: _tokenize(t) for b, t in bloc_corpus.items()}

        result: Dict[str, Dict[str, float]] = {}

        for b1 in blocs:
            result[b1] = {}
            for b2 in blocs:
                if b1 == b2:
                    result[b1][b2] = 0.0
                else:
                    result[b1][b2] = round(d, 3)

        return result
