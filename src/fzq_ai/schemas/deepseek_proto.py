"""DeepSeek Proto-Schema — Pydantic models for the Structure Layer output.

Pipeline: GLM → DeepSeek(Structure) → Minimax(Validation) → 豆包 → Kimi → Qwen

These models define the contract that DeepSeek must produce
and Minimax must validate.
"""

from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class DeepSeekFact(BaseModel):
    """5W1H fact extracted from GLM raw material."""
    who: str = ""
    what: str = ""
    when: str = ""
    where: str = ""
    why: str = ""
    how: str = ""


class DeepSeekEvent(BaseModel):
    """Layered event chain entry."""
    level: int = 1          # 1=primary, 2=secondary, 3=tertiary
    summary: str = ""
    actors: List[str] = Field(default_factory=list)


class DeepSeekRiskCategory(BaseModel):
    """Five-category risk classification."""
    political: List[str] = Field(default_factory=list)
    economic: List[str] = Field(default_factory=list)
    social: List[str] = Field(default_factory=list)
    tech: List[str] = Field(default_factory=list)
    international: List[str] = Field(default_factory=list)


class DeepSeekProtoSchema(BaseModel):
    """
    Complete DeepSeek Proto-Schema output.

    This is the contract between DeepSeek (Structure Layer)
    and Minimax (Validation Layer).
    """
    facts: List[DeepSeekFact] = Field(default_factory=list)
    events: List[DeepSeekEvent] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    narratives: List[str] = Field(default_factory=list)
    risks: DeepSeekRiskCategory = Field(default_factory=DeepSeekRiskCategory)
    policy: List[str] = Field(default_factory=list)
    trend: List[str] = Field(default_factory=list)
    raw_quotes: List[str] = Field(default_factory=list)
