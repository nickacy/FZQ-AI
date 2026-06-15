# fzq_ai/agents/news_intel_agent.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fzq_ai.agents.base_agent import BaseAgent
from fzq_ai.intel.news_intel_service import (
    NewsIntelService,
    NewsIntelConfig,
)
from fzq_ai.intel.models import IntelBundle

class NewsIntelAgent(BaseAgent):
    """
    """

    def __init__(self) -> None:
        # 从根目录加载 rss_sources.yaml
        self._service = NewsIntelService(config)

    async def run(
        self,
        """
        """
        bundle: IntelBundle = await self._service.gather_intel(
            topics=topics or ["geopolitics", "macro", "tech"],
            depth="deep" if depth == "deep" else "fast",

        return {
            "query": query,
            "intel_bundle": bundle,
