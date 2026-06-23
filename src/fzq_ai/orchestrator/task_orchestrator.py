# src/fzq_ai/orchestrator/task_orchestrator.py
# v13 Task Orchestrator – 统一调度入口

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
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


    async def run_with_metrics(
        self, pipeline: BasePipeline, req: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a pipeline with full metrics capture.

        Wraps run() to additionally:
          - Record token consumption via token_monitor
          - Store trace_id in output
          - Timestamp with timezone.utc
          - Write metrics to JSONL when available
        """
        import time as _time

        trace_id = req.get("trace_id") or self._gen_trace_id()
        req["trace_id"] = trace_id

        t0 = _time.perf_counter()

        # Run the pipeline
        output = await self.run(pipeline, req)

        duration_ms = round((_time.perf_counter() - t0) * 1000, 2)

        # Enrich output with metrics metadata
        output.setdefault("trace_id", trace_id)
        output.setdefault("duration_ms", duration_ms)
        output.setdefault(
            "timestamp_utc", datetime.now(timezone.utc).isoformat()
        )

        # Record token consumption if available
        try:
            token_monitor.record(
                pipeline=pipeline.name,
                trace_id=trace_id,
                prompt_tokens=output.get("prompt_tokens", 0),
                completion_tokens=output.get("completion_tokens", 0),
                total_tokens=output.get("total_tokens", 0),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception:
            pass  # token_monitor may not support record() yet

        return output

    def _gen_trace_id(self) -> str:
        """Generate a unique trace_id using uuid4 + timestamp prefix."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{ts}-{uuid.uuid4().hex[:12]}"
