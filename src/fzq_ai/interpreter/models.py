"""Kimi Interpretation Layer — Pydantic models for explanation output."""

from __future__ import annotations
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ExplanationResult(BaseModel):
    """Kimi interpreter output — human-readable explanations from structured data.

    Does NOT alter facts, supplement fields, or invent content.
    """
    policy_brief: str = ""
    risk_summary: str = ""
    narrative_analysis: str = ""
    trend_insights: str = ""
    quotes_analysis: str = ""
    structured_explanation: Dict[str, Any] = Field(default_factory=dict)
