# src/fzq_ai/orchestrator/task_orchestrator.py
# v13 Orchestrator – unified trace_id, metrics, pipeline execution

from __future__ import annotations

import uuid
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fzq_ai.monitor.metrics import metrics
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline


class TaskOrchestrator:
    """
    v13 Orchestrator

    - 为每个任务生成 trace_id
    - 顺序执行多个 pipelines
    - 调用 pipeline.run_with_metrics()
    - 记录 orchestrator 级 metrics
    """

    def __init__(self):
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload 示例：
        {
            "query": "测试",
            "user_id": "...",
        }
        """
        trace_id = str(uuid.uuid4())
        start = time.time()

        context = {
            "query": payload.get("query"),
            "trace_id": trace_id,
            "user_id": payload.get("user_id"),
        }

        results = {}

        # ---------------- Pipeline 1: News ----------------
        news_result = await self.news.run_with_metrics(context=context, trace_id=trace_id)
        results["news"] = news_result

        # ---------------- Pipeline 2: Risk ----------------
        risk_result = await self.risk.run_with_metrics(context=context, trace_id=trace_id)
        results["risk"] = risk_result

        # ---------------- Pipeline 3: Sentiment ----------------
        sentiment_result = await self.sentiment.run_with_metrics(context=context, trace_id=trace_id)
        results["sentiment"] = sentiment_result

        # ---------------- Orchestrator metrics ----------------
        duration_ms = (time.time() - start) * 1000
        metrics.record(
            name="orchestrator",
            duration_ms=duration_ms,
            extra={
                "trace_id": trace_id,
                "pipelines": ["news", "risk", "sentiment"],
            },
        )

        return {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }


# 单例
orchestrator = TaskOrchestrator()
