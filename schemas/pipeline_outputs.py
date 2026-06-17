from typing import List, Optional
from pydantic import BaseModel


# -------------------------
# NewsPipeline Schema
# -------------------------
class NewsEvent(BaseModel):
    title: str
    date: Optional[str]
    region: Optional[str]
    summary: Optional[str]


class NewsIntelOutput(BaseModel):
    language: str
    regions: List[str]
    events: List[NewsEvent]
    stats: dict


# -------------------------
# RiskPipeline Schema
# -------------------------
class RiskOutput(BaseModel):
    summary: str
    factors: str
    forecast: str


# -------------------------
# SentimentPipeline Schema
# -------------------------
class SentimentOutput(BaseModel):
    score: str
    summary: str


# -------------------------
# NarrativePipeline Schema
# -------------------------
class NarrativeOutput(BaseModel):
    summary: str
    key_points: str
    storyline: str
    implications: str


# -------------------------
# ScenarioPipeline Schema
# -------------------------
class ScenarioOutput(BaseModel):
    scenarios: str  # 仍然是 LLM 文本输出


# -------------------------
# DailyReportPipeline Schema
# -------------------------
class DailyReportOutput(BaseModel):
    news: NewsIntelOutput
    risk: RiskOutput
    sentiment: SentimentOutput
    narrative: NarrativeOutput
    scenario: ScenarioOutput
