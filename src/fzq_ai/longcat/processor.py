# src/fzq_ai/longcat/processor.py
# V24-Final — LongCatProcessor (Strategy Pattern)
"""
Unified long-text processor for FZQ-AI.
Supports pluggable strategies (v2 default).
All pipelines and agents MUST use this processor.
"""
from __future__ import annotations
from typing import List, Optional


class LongCatV2Strategy:
    """V2 default: chunk by paragraphs, summarize by concatenation."""

    MAX_CHUNK_SIZE: int = 4096

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []
        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current: str = ""
        for para in paragraphs:
            if len(current) + len(para) < self.MAX_CHUNK_SIZE:
                current += para + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = para + "\n\n"
        if current.strip():
            chunks.append(current.strip())
        return chunks or [text]

    def summarize(self, chunks: List[str]) -> str:
        return "\n---\n".join(chunks[:5])


class LongCatProcessor:
    """Unified entry point for long-text chunking & summarization."""

    def __init__(self, strategy: str = "v2"):
        self.strategy = strategy
        self.impl = self._load_strategy(strategy)

    def _load_strategy(self, strategy: str):
        if strategy == "v2":
            return LongCatV2Strategy()
        raise ValueError(f"Unknown LongCat strategy: {strategy}")

    def chunk(self, text: str) -> List[str]:
        return self.impl.chunk(text)

    def summarize(self, chunks: List[str]) -> str:
        return self.impl.summarize(chunks)
