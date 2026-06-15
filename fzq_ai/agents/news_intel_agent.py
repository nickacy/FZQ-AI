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
    多源 News Intake Agent：
    - 直接调用 NewsIntelService
    - 返回结构化 IntelBundle
    """

    name: str = "news-intel"
    description: str = "多源新闻抓取 + 翻译 + 去噪 + 事件聚类 + 叙事视图"

    def __init__(self) -> None:
        # 从根目录加载 rss_sources.yaml
        config = NewsIntelConfig.from_yaml("rss_sources.yaml")
        self._service = NewsIntelService(config)

    async def run(
        self,
        query: str,
        topics: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        depth: str = "fast",
    ) -> Dict[str, Any]:
        """
        :param query: 用户查询（目前主要用于日志/后续扩展）
        :param topics: 主题过滤
        :param regions: 区域过滤
        :param depth: 'fast' | 'deep'
        """
        bundle: IntelBundle = await self._service.gather_intel(
            topics=topics or ["geopolitics", "macro", "tech"],
            regions=regions,
            depth="deep" if depth == "deep" else "fast",
        )

        return {
            "query": query,
            "intel_bundle": bundle,
        }
