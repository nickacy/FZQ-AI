# src/fzq_ai/llm/providers/deepseek_provider.py
# v13 DeepSeek Provider – unified output, metrics, token_monitor

from __future__ import annotations

import time
from typing import Any, Dict

from fzq_ai.metrics.metrics import metrics
from fzq_ai.monitor.token_monitor import token_monitor


class DeepSeekProvider:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    async def run(self, req: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        provider_name = "deepseek"
        model_name = self.model

        try:
            # ---- 调用 DeepSeek API ----
            response = await self.client.chat(req)

            output = response["content"]
            prompt_tokens = response["usage"]["prompt_tokens"]
            completion_tokens = response["usage"]["completion_tokens"]
            total_tokens = prompt_tokens + completion_tokens

            success = True

        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            metrics.record_provider_call(
                provider=provider_name,
                model=model_name,
                duration_ms=duration_ms,
                success=False,
                extra={"error": str(e)},
            )
            return {"error": str(e)}

        # ---- metrics ----
        duration_ms = (time.time() - start) * 1000
        metrics.record_provider_call(
            provider=provider_name,
            model=model_name,
            duration_ms=duration_ms,
            success=True,
        )

        # ---- token monitor ----
        cost_usd = total_tokens / 1000 * 0.002
        token_monitor.record(
            provider=provider_name,
            model=model_name,
            task_type=req.get("task_type", "unknown"),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost_usd,
            trace_id=req.get("trace_id"),
        )

        # ---- 返回统一结构 ----
        return {
            "output": output,
            "model": model_name,
            "provider": provider_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }
