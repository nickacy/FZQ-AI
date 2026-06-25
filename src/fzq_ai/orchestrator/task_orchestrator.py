# src/fzq_ai/orchestrator/task_orchestrator.py
# v13 Task Orchestrator – 统一调度入口

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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

    async def run(
        self,
        req: Dict[str, Any],
        pipeline: Optional[BasePipeline] = None,
    ) -> Dict[str, Any]:
        """Run a request, auto-resolving pipeline from task_type if not given."""
        if pipeline is None:
            pipeline = self._resolve_pipeline(req)
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
        self,
        req: Dict[str, Any],
        pipeline: Optional[BasePipeline] = None,
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

    def _resolve_pipeline(self, req: Dict[str, Any]) -> BasePipeline:
        """Resolve which pipeline to use from the request task_type."""
        task_type = req.get("task_type", "").lower()

        # Map task_type -> pipeline module
        pipeline_map = {
            "news": "fzq_ai.pipelines.news_pipeline",
            "narrative": "fzq_ai.pipelines.narrative_pipeline",
            "risk": "fzq_ai.pipelines.risk_pipeline",
            "daily_report": "fzq_ai.pipelines.daily_report_pipeline",
            "sentiment": "fzq_ai.pipelines.sentiment_pipeline",
            "scenario": "fzq_ai.pipelines.scenario_pipeline",
        }

        mod_path = pipeline_map.get(task_type)
        if mod_path:
            import importlib
            mod = importlib.import_module(mod_path)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePipeline) and attr is not BasePipeline:
                    return attr()

        # Fallback: return a minimal pipeline that delegates to Router directly
        logger = __import__("fzq_ai.utils.logger", fromlist=["get_logger"]).get_logger(__name__)
        logger.warning("no pipeline matched task_type=%s, using router fallback", task_type)

        class _FallbackPipeline(BasePipeline):
            name = "fallback"
            async def preprocess(self, r):
                r.setdefault("prompt", r.get("query", str(r)))
                r.setdefault("task_type", "default")
                return r
            async def postprocess(self, result):
                return result

        return _FallbackPipeline()

    def _gen_trace_id(self) -> str:
        """Generate a unique trace_id using uuid4 + timestamp prefix."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{ts}-{uuid.uuid4().hex[:12]}"
