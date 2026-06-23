# src/fzq_ai/orchestrator/task_orchestrator.py
# v13 Task Orchestrator – 统一调度入口

from __future__ import annotations

import time
from typing import Any, Dict

from fzq_ai.metrics.metrics import metrics
from fzq_ai.monitor.token_monitor import token_monitor
from fzq_ai.llm.router import Router
from fzq_ai.pipelines.base import BasePipeline


class TaskOrchestrator:
    """
    v13 任务调度器
    - 统一 trace_id
    - 统一 pipeline 调度
    - 统一 provider 调用
    - 统一 metrics + token_monitor
    """

    def __init__(self):
        self.router = Router()

    async def run(self, pipeline: BasePipeline, req: Dict[str, Any]) -> Dict[str, Any]:
        trace_id = req.get("trace_id") or self._gen_trace_id()
        req["trace_id"] = trace_id

        start = time.time()

        # ---- Pipeline 前置处理 ----
        preprocessed = await pipeline.preprocess(req)

        # ---- Router 调用 Provider ----
        result = await self.router.run(preprocessed)

        # ---- Pipeline 后置处理 ----
        final_output = await pipeline.postprocess(result)

        duration_ms = (time.time() - start) * 1000

        # ---- Orchestrator 级别 metrics ----
        metrics.record_orchestrator_call(
            pipeline=pipeline.name,
            duration_ms=duration_ms,
            success=("error" not in final_output),
            trace_id=trace_id,
        )

        return final_output

    def _gen_trace_id(self) -> str:
        return f"trace-{int(time.time() * 1000)}"
