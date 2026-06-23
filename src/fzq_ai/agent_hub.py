# fzq_ai/agent_hub.py
"""
AgentHub - Unified Agent Dispatch Center
- Manages LLM routing and all Pipelines
- Provides unified run_* entry points
"""

import asyncio
from typing import List, Dict, Any, Optional

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.domain.models import Article


class AgentHub:
    """Unified Agent Dispatch Center."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.router = LLMRouter()

        self.news_pipeline = NewsPipeline()
        self.narrative_pipeline = NarrativePipeline()
        self.risk_pipeline = RiskPipeline()
        self.daily_report_pipeline = DailyReportPipeline()

    # ---------------- Task entry points (sync wrappers) ----------------

    def run_news(self, topic: str = "") -> Dict[str, Any]:
        """News fetching: synchronous wrapper."""
        result = self.news_pipeline.run(topic)
        return {"success": result.success, "data": result.data, "error": result.error}

    def run_narrative(self, items: List[str]) -> Dict[str, Any]:
        """Narrative analysis: convert string list to Article list then analyze."""
        articles = [
            Article(title_original=item, content_original=item) for item in items
        ]
        result = asyncio.run(self.narrative_pipeline.run(articles=articles))
        return {"success": result.success, "data": result.data, "error": result.error}

    def run_risk(self, items: List[str]) -> Dict[str, Any]:
        """Risk analysis: convert string list to Article list then analyze."""
        articles = [Article(title_original=item) for item in items]
        result = asyncio.run(self.risk_pipeline.run(articles=articles))
        return {"success": result.success, "data": result.data, "error": result.error}

    def run_daily_report(self, items: List[str]) -> Dict[str, Any]:
        """Daily report: convert string list to Article list then generate report."""
        articles = [Article(title_original=item) for item in items]
        result = asyncio.run(self.daily_report_pipeline.run(articles=articles))
        return {"success": result.success, "data": result.data, "error": result.error}

    # ---------------- Metrics output ----------------

    def get_metrics(self) -> Dict[str, Any]:
        """Return call statistics (compatible across LLMRouter implementations)."""
        return {
            "llm_router": str(type(self.router).__name__),
            "pipelines": [
                "news_pipeline",
                "narrative_pipeline",
                "risk_pipeline",
                "daily_report_pipeline",
            ]
        }
