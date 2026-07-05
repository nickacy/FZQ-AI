"""src/fzq_ai/minimax/schema.py

Strict Schema definition for FZQ-AI (V24.3.1+).

Mirrors the Proto-Schema produced by DeepSeek, with:
  - All fields required (but defaults are empty lists/objects, so input may be sparse)
  - All list fields use `List[str]` (facts/events/actors/narratives/policy/trend/raw_quotes)
  - Nested `risks` is itself a BaseModel with 5 sub-categories (all List[str])
  - Field order is fixed (see STRICT_SCHEMA_FIELD_ORDER)

This is the *final structural baseline* — anything downstream (豆包/Kimi/Qwen)
assumes every field exists with the correct type.
"""
from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class StrictRisks(BaseModel):
    """Nested risk categorization. All 5 sub-fields are List[str]."""
    political: List[str] = Field(default_factory=list)
    economic: List[str] = Field(default_factory=list)
    social: List[str] = Field(default_factory=list)
    tech: List[str] = Field(default_factory=list)
    international: List[str] = Field(default_factory=list)


class StrictSchema(BaseModel):
    """FZQ-AI final strict schema. 13 top-level fields + nested risks (5 fields)."""
    facts: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    narratives: List[str] = Field(default_factory=list)
    risks: StrictRisks = Field(default_factory=StrictRisks)
    policy: List[str] = Field(default_factory=list)
    trend: List[str] = Field(default_factory=list)
    raw_quotes: List[str] = Field(default_factory=list)


# Canonical field order — used by validator to guarantee stable key ordering
# in repaired output (R5: maintain field name consistency).
STRICT_SCHEMA_FIELD_ORDER = [
    "facts",
    "events",
    "actors",
    "narratives",
    "risks",
    "policy",
    "trend",
    "raw_quotes",
]

STRICT_RISKS_FIELD_ORDER = [
    "political",
    "economic",
    "social",
    "tech",
    "international",
]