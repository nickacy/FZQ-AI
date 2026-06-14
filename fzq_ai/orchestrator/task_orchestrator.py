"""
Task Orchestrator — unified pipeline scheduler.
Fixed: no nested asyncio.run(), proper error propagation, unified return types.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from fzq_ai.domain.models import Article, ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline


class TaskOrchestrator:
    """Unified scheduler for all pipelines with LLM router sharing."""

    def __init__(self, agent_hub: Any = None):
        # Share a single LLMRouter across all pipelines
        if agent_hub is not None:
            self.router = agent_hub.router
        else:
            self.router = LLMRouter()

        self.pipelines = {
            "news-intel": NewsPipeline(llm_router=self.router),
            "narrative": NarrativePipeline(llm_router=self.router),
            "risk": RiskPipeline(llm_router=self.router),
            "daily-report": DailyReportPipeline(llm_router=self.router),
        }

    # ── Public API (returns dict for backward compat) ───────────

    def run(
        self,
        agent_name: str,
        items: Optional[list] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Synchronous entry point. Delegates to async impl without nested loops."""
        if items is None:
            items = []

        articles = [Article(title_original=str(i)) for i in items]

        # Map agent names to pipeline keys
        agent_map = {
            "daily_report": "daily-report",
            "daily-report": "daily-report",
            "narrative": "narrative",
            "risk": "risk",
            "news-intel": "news-intel",
            "news_intel": "news-intel",
        }

        pipeline_key = agent_map.get(agent_name) or agent_name

        if pipeline_key not in self.pipelines:
            return {"success": False, "error": f"Unknown agent: {agent_name}"}

        pipeline = self.pipelines[pipeline_key]

        try:
            # Handle news-intel differently (uses .run() not .run(articles=))
            if pipeline_key == "news-intel":
                topic = " ".join(items) if items else kwargs.get("topic", "")
                result: ServiceResult = pipeline.run(topic=topic)
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                }

            # Async pipelines: use a safe runner that detects existing loops
            result: ServiceResult = _run_async_safely(
                pipeline.run(articles=articles, **kwargs)
            )
            return {
                "success": result.success,
                "data": result.data,
                "error": result.error,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_agent(
        self,
        agent_name: str,
        articles: Optional[list] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Backward-compatible wrapper. Returns dict always."""
        return self.run(agent_name, items=None, articles=articles, **kwargs)

    @property
    def router_metrics(self) -> dict:
        """Expose LLM router metrics for monitoring."""
        return self.router.metrics


def _run_async_safely(coro: Any) -> Any:
    """
    Run an async coroutine safely — works even if there's already a running loop.
    Avoids 'This event loop is already running' errors.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to use asyncio.run()
        return asyncio.run(coro)

    # There's already a running loop — use nest_asyncio or thread-based workaround
    import concurrent.futures

    def _run_in_thread():
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_in_thread)
        return future.result()
