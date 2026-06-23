# src/fzq_ai/pipelines/base.py
# v13 BasePipeline 鈥?鎵€鏈?Pipeline 鐨勭粺涓€鍩虹被

from __future__ import annotations
from typing import Any, Dict


class BasePipeline:
    """
    v13 Pipeline 缁熶竴鎺ュ彛
    - preprocess锛氳姹傞澶勭悊
    - postprocess锛氱粨鏋滃悗澶勭悊
    - name锛歱ipeline 鍚嶇О锛堢敤浜?metrics锛?
    """

    name: str = "base"

    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        瀛愮被鍙噸鍐欙細
        - 娣诲姞 task_type
        - 娣诲姞 prompt 妯℃澘
        - 娣诲姞涓婁笅鏂?
        """
        return req

    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        瀛愮被鍙噸鍐欙細
        - 娓呮礂杈撳嚭
        - 缁撴瀯鍖栫粨鏋?
        - 閿欒澶勭悊
        """
        return result


    # 鈹€鈹€ v13 core methods 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Main pipeline execution flow.

        Lifecycle:
            1. validate_inputs()   鈫?input validation
            2. preprocess(req)     鈫?build prompt & context
            3. llm_call(prompt)    鈫?invoke LLM (subclass override)
            4. postprocess(result) 鈫?clean & structure output
            5. finalize(output)    鈫?cleanup / logging
        """
        import time
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

            # 3. LLM call (subclass provides)
            result = await self.call_llm(req)

            # 4. Postprocess
            output = await self.postprocess(result)

            # 5. Finalize
            await self.finalize(output)

            output["trace_id"] = trace_id
            output["duration_ms"] = round((time.perf_counter() - t_start) * 1000, 2)
            output.setdefault("status", "success")

            logger.info("pipeline_done", name=self.name, trace_id=trace_id,
                        duration_ms=output["duration_ms"])
            return output

        except Exception as e:
            logger.error("pipeline_failed", name=self.name, trace_id=trace_id, error=str(e))
            return {
                "status": "error",
                "errors": [str(e)],
                "trace_id": trace_id,
            }

    async def run_with_metrics(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Run the pipeline and collect performance metrics.

        Wraps run() to capture:
          - token usage (prompt_tokens, completion_tokens)
          - timing (preprocess_ms, llm_ms, postprocess_ms, total_ms)
          - status & trace_id

        Metrics are logged and optionally written to JSONL.
        """
        import time
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

        # Optionally write to JSONL
        try:
            from fzq_ai.metrics.metrics_writer import write_metrics_jsonl
            write_metrics_jsonl(metrics)
        except (ImportError, Exception):
            pass  # metrics writer not available 鈥?skip

        return output

    # 鈹€鈹€ Override hooks 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def validate_inputs(self, kwargs: Dict[str, Any]) -> list:
        """Validate input parameters. Return list of error strings."""
        return []

    async def call_llm(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """LLM call hook 鈥?subclasses must override or inject a router."""
        raise NotImplementedError(
            f"{self.name}: call_llm() must be overridden or a router injected"
        )

    async def finalize(self, output: Dict[str, Any]) -> None:
        """Cleanup hook. Called after postprocess."""
        pass

