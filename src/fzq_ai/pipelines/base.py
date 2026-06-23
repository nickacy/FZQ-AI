# src/fzq_ai/pipelines/base.py
# FZQ‑AI v13 BasePipeline — unified pipeline base class

from __future__ import annotations
import uuid
import time
from typing import Any, Dict, List


class BasePipeline:
    """
    FZQ‑AI v13 unified pipeline interface.

    Lifecycle:
        1. validate_inputs()   → validate incoming kwargs
        2. preprocess()        → build request payload / prompt
        3. call_llm()          → invoke LLM (subclass override)
        4. postprocess()       → clean & structure output
        5. finalize()          → logging / cleanup

    All pipelines (English + Chinese) inherit from this class.
    """

    name: str = "base_pipeline"

    # ----------------------------------------------------------------------
    # Input validation
    # ----------------------------------------------------------------------
    def validate_inputs(self, kwargs: Dict[str, Any]) -> List[str]:
        """
        Validate input parameters.
        Subclasses may override.
        Return a list of error messages.
        """
        return []

    # ----------------------------------------------------------------------
    # Preprocess
    # ----------------------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses may override.
        Typical tasks:
            - add task_type
            - build prompt template
            - enrich context
        """
        return req

    # ----------------------------------------------------------------------
    # LLM call (must be overridden)
    # ----------------------------------------------------------------------
    async def call_llm(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses MUST override or inject a router.
        """
        raise NotImplementedError(
            f"{self.name}: call_llm() must be implemented by subclass"
        )

    # ----------------------------------------------------------------------
    # Postprocess
    # ----------------------------------------------------------------------
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses may override.
        Typical tasks:
            - clean output
            - convert to structured schema
            - error normalization
        """
        return result

    # ----------------------------------------------------------------------
    # Finalize
    # ----------------------------------------------------------------------
    async def finalize(self, output: Dict[str, Any]) -> None:
        """
        Cleanup hook.
        Subclasses may override.
        """
        pass

    # ----------------------------------------------------------------------
    # Core execution (async)
    # ----------------------------------------------------------------------
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Main pipeline execution flow.

        Steps:
            1. validate_inputs()
            2. preprocess()
            3. call_llm()
            4. postprocess()
            5. finalize()
        """
        from fzq_ai.utils.logger import get_logger

        logger = get_logger(__name__)
        trace_id = kwargs.pop("trace_id", str(uuid.uuid4()))
        t_start = time.perf_counter()

        logger.info("pipeline_start", name=self.name, trace_id=trace_id)

        try:
            # 1. Validate
            errors = self.validate_inputs(kwargs)
            if errors:
                return {
                    "status": "error",
                    "errors": errors,
                    "trace_id": trace_id,
                }

            # 2. Preprocess
            req = await self.preprocess(dict(kwargs))

            # 3. LLM call
            result = await self.call_llm(req)

            # 4. Postprocess
            output = await self.postprocess(result)

            # 5. Finalize
            await self.finalize(output)

            # Metadata
            output["trace_id"] = trace_id
            output["duration_ms"] = round((time.perf_counter() - t_start) * 1000, 2)
            output.setdefault("status", "success")

            logger.info(
                "pipeline_done",
                name=self.name,
                trace_id=trace_id,
                duration_ms=output["duration_ms"],
            )

            return output

        except Exception as e:
            logger.error(
                "pipeline_failed",
                name=self.name,
                trace_id=trace_id,
                error=str(e),
            )
            return {
                "status": "error",
                "errors": [str(e)],
                "trace_id": trace_id,
            }

    # ----------------------------------------------------------------------
    # Metrics wrapper
    # ----------------------------------------------------------------------
    async def run_with_metrics(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Wrap run() and collect performance metrics.

        Captures:
            - total_duration_ms
            - token usage (if provided by subclass)
            - status
            - trace_id
        """
        from fzq_ai.utils.logger import get_logger

        logger = get_logger(__name__)
        trace_id = kwargs.get("trace_id", str(uuid.uuid4()))
        t_total = time.perf_counter()

        # Run pipeline
        output = await self.run(trace_id=trace_id, **kwargs)

        # Build metrics payload
        total_ms = round((time.perf_counter() - t_total) * 1000, 2)
        metrics = {
            "pipeline": self.name,
            "trace_id": trace_id,
            "status": output.get("status", "unknown"),
            "total_duration_ms": total_ms,
            "prompt_tokens": output.get("prompt_tokens", 0),
            "completion_tokens": output.get("completion_tokens", 0),
            "total_tokens": output.get("total_tokens", 0),
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        }

        # Log metrics
        logger.info("pipeline_metrics", **metrics)

        # Optional JSONL writer
        try:
            from fzq_ai.metrics.metrics_writer import write_metrics_jsonl
            write_metrics_jsonl(metrics)
        except Exception:
            pass

        return output
