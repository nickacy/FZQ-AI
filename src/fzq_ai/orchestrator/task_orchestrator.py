# fzq_ai/orchestrator/task_orchestrator.py
# FZQ‑AI v13 Orchestrator（支持 DAG + Metrics + 并发）

import asyncio
import time
import uuid
from typing import Dict, Any

from fzq_ai.monitor.metrics import metrics
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline


class TaskOrchestrator:
    """
    v13 Orchestrator
    - 统一 run_with_metrics(payload)
    - 支持任务依赖图（Task Graph）
    - 支持并发执行
    - 自动记录 orchestrator-level metrics
    """

    def __init__(self):
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()

    # ---------------------------------------------------------
    # v13：统一入口（payload-based）
    # ---------------------------------------------------------
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        start = time.time()

        # -----------------------------------------------------
        # Task Graph（v13 简化版 DAG）
        # news → risk → sentiment
        # -----------------------------------------------------
        news_task = asyncio.create_task(
            self.news.run_with_metrics({"query": payload["query"], "trace_id": trace_id})
        )

        # risk 依赖 news
        risk_task = asyncio.create_task(self._run_after(news_task, self.risk, payload, trace_id))

        # sentiment 依赖 risk
        sentiment_task = asyncio.create_task(self._run_after(risk_task, self.sentiment, payload, trace_id))

        # 等待所有任务完成
        news_result, risk_result, sentiment_result = await asyncio.gather(
            news_task, risk_task, sentiment_task
        )

        # -----------------------------------------------------
        # Orchestrator-level metrics
        # -----------------------------------------------------
        metrics.record(
            name="orchestrator_total",
            duration=time.time() - start,
            extra={"trace_id": trace_id}
        )

        return {
            "trace_id": trace_id,
            "news": news_result,
            "risk": risk_result,
            "sentiment": sentiment_result,
        }

    # ---------------------------------------------------------
    # Helper：等待前置任务完成后再执行 pipeline
    # ---------------------------------------------------------
    async def _run_after(self, dependency_task, pipeline, payload, trace_id):
        await dependency_task
        return await pipeline.run_with_metrics({"query": payload["query"], "trace_id": trace_id})


# ---------------------------------------------------------
# CLI 入口（可选）
# ---------------------------------------------------------
if __name__ == "__main__":
    orch = TaskOrchestrator()
    result = asyncio.run(orch.run({"query": "测试"}))
    print(result)
