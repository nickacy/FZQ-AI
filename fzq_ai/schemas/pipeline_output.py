# fzq_ai/schemas/pipeline_outputs.py
"""Unified Pydantic schemas for all pipeline outputs."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class NewsPipelineOutput(BaseModel):
    """Output schema for NewsPipeline."""
    summary: str = Field(..., description="LLM-generated intelligence summary")
    article_count: int = Field(default=0, description="Number of articles fetched")
    articles: List[Dict[str, Any]] = Field(default_factory=list, description="Article metadata list")
    regions_covered: List[str] = Field(default_factory=list)
    languages_detected: List[str] = Field(default_factory=list)


class RiskPipelineOutput(BaseModel):
    """Output schema for RiskPipeline."""
    summary: str = Field(..., description="Risk assessment summary")
    factors: str = Field(default="", description="Key risk factors")
    forecast: str = Field(default="", description="30-day risk trend forecast")
    risk_score: Optional[float] = Field(default=None, description="Computed risk score 0-100")


class SentimentPipelineOutput(BaseModel):
    """Output schema for SentimentPipeline."""
    score: str = Field(default="neutral", description="Sentiment score (-1 to +1)")
    summary: str = Field(default="", description="Sentiment tendency summary")
    distribution: Dict[str, int] = Field(default_factory=dict, description="positive/neutral/negative counts")


class NarrativePipelineOutput(BaseModel):
    """Output schema for NarrativePipeline."""
    summary: str = Field(..., description="Narrative summary")
    key_points: str = Field(default="", description="5 key narrative points")
    storyline: str = Field(default="", description="Clear storyline")
    implications: str = Field(default="", description="30-day implications")


class ScenarioPipelineOutput(BaseModel):
    """Output schema for ScenarioPipeline."""
    scenarios: str = Field(..., description="3 scenario descriptions with risk levels")


class DailyReportOutput(BaseModel):
    """Output schema for DailyReportPipeline."""
    news: Any = Field(default="", description="News section")
    risk: Any = Field(default="", description="Risk section")
    sentiment: Any = Field(default="", description="Sentiment section")
    narrative: Any = Field(default="", description="Narrative section")
    scenario: Any = Field(default="", description="Scenario section")
