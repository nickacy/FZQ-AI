from __future__ import annotations
import uuid
import time
from typing import Any, Dict, List, Optional, Generic, TypeVar
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class PipelineResult(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None


class BasePipeline(Generic[T]):
    """
    FZQ‑AI v13 unified pipeline interface with full generic support.
    Allows: class MyPipeline(BasePipeline[MyOutput])
    """

    name: str = "base_pipeline"

    # ----------------------------------------------------------------------
    # Input validation
    # ----------------------------------------------------------------------
    def validate_inputs(self, kwargs: Dict[str, Any]) -> List[str]:
        return []

    # ----------------------------------------------------------------------
    # Preprocess
    # ----------------------------------------------------------------------
    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        return req

    # ----------------------------------------------------------------------
    # LLM call (must be overridden)
    # ----------------------------------------------------------------------
    async def call_llm(self, req: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError(
            f"{self.name}: call_llm() must be implemented by subclass"
        )

    # ----------------------------------------------------------------------
    # Postprocess
    # ----------------------------------------------------------------------
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return result

    # ----------------------------------------------------------------------
    # Finalize
    # ----------------------------------------------------------------------
    async def finalize(self, output: Dict[str, Any]) -> None:
        pass

    # ----------------------------------------------------------------------
    # Core execution (async)
    # ----------------------------------------------------------------------
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
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
            raw = await self.call_llm(req)

            # 4. Postprocess
            output = await self.postprocess(raw)

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
        from fzq_ai.utils.logger import get_logger

        logger = get_logger(__name__)
        trace_id = kwargs.get("trace_id", str(uuid.uuid4()))
        t_total = time.perf_counter()

        output = await self.run(trace_id=trace_id, **kwargs)

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

        logger.info("pipeline_metrics", **metrics)

        try:
            from fzq_ai.metrics.metrics_writer import write_metrics_jsonl
            write_metrics_jsonl(metrics)
        except Exception:
            pass

        return output
