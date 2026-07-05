"""GLM-5 Turbo Schema — Pydantic models for the Content Extraction Layer.

Pipeline: GLM(raw text) → DeepSeek(structure) → Minimax(validate) → ...

These 8 models define what GLM extracts from multilingual news text.
They are the raw material that feeds the downstream pipeline.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class GLMCoreFact(BaseModel):
    """5W1H fact — GLM extracts these from raw news text."""
    who: str = ""
    what: str = ""
    when: str = ""
    where: str = ""
    why: str = ""
    how: str = ""


class GLMEvent(BaseModel):
    """Single event in an event chain."""
    level: int = 1                     # 1=primary, 2=secondary
    summary: str = ""
    actors: List[str] = Field(default_factory=list)
    related_events: List[str] = Field(default_factory=list)


class GLMActor(BaseModel):
    """Named entity or organization mentioned in the text."""
    name: str = ""
    role: str = ""                     # e.g. government, corporation, NGO
    mentions: int = 1
    quotes: List[str] = Field(default_factory=list)


class GLMNarrative(BaseModel):
    """Narrative line detected in the text."""
    theme: str = ""
    stance: str = ""                   # e.g. positive, negative, neutral
    confidence: float = 0.0
    supporting_sentences: List[str] = Field(default_factory=list)


class GLMRisk(BaseModel):
    """Single risk signal classified into one of 5 categories."""
    category: str = ""                 # political, economic, social, tech, international
    description: str = ""
    severity: str = ""                 # low, medium, high, critical
    source_sentence: str = ""


class GLMPolicySignal(BaseModel):
    """Policy-relevant signal from the text."""
    signal: str = ""
    domain: str = ""                   # e.g. trade, defense, environment
    direction: str = ""               # e.g. tightening, loosening, new


class GLMTrendSignal(BaseModel):
    """Trend / pattern signal."""
    trend: str = ""
    time_horizon: str = ""            # e.g. short-term, medium-term, long-term
    indicators: List[str] = Field(default_factory=list)


class GLMRawQuote(BaseModel):
    """Verbatim quote from the source text."""
    text: str = ""
    speaker: str = ""
    language: str = ""                # detected language code
    context_sentence: str = ""


class GLMRawMaterial(BaseModel):
    """
    Complete GLM extraction output — the raw material for downstream pipelines.

    8 fields as specified: core_facts, event_chain, actors, narratives,
    risks, policy_signals, trend_signals, raw_quotes.
    """
    source_text: str = ""              # original input text (preserved)
    detected_language: str = ""        # e.g. zh, en, ar
    core_facts: List[GLMCoreFact] = Field(default_factory=list)
    event_chain: List[GLMEvent] = Field(default_factory=list)
    actors: List[GLMActor] = Field(default_factory=list)
    narratives: List[GLMNarrative] = Field(default_factory=list)
    risks: List[GLMRisk] = Field(default_factory=list)
    policy_signals: List[GLMPolicySignal] = Field(default_factory=list)
    trend_signals: List[GLMTrendSignal] = Field(default_factory=list)
    raw_quotes: List[GLMRawQuote] = Field(default_factory=list)


# Ensure forward references resolve
GLMRawMaterial.model_rebuild()
