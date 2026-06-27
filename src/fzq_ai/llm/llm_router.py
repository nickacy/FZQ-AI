# fzq_ai/llm/llm_router.py
# v13 Compatibility Layer for old pipelines

from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.llm.router import Router


class LLMRouter:
    """
    v13 Compatibility layer:
    - Retains legacy interface: route(task_name, prompt)
    - Underlying calls v13 Router.run(req)
    """

    def __init__(self):
        self.router = Router()

    async def route(self, task_type: str, prompt: str) -> str:
        req = {
            "task_type": task_type,
            "prompt": prompt,
        }
        result = await self.router.run(req)
        return result.get("output", "")

    async def call(
        self,
        provider: str,
        prompt: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 60,
    ) -> str:
        """
        v13 unified call() interface used by LLMExecutor.
        Routes to the appropriate provider and returns text output.
        """
        req = {
            "task_type": "chat",
            "prompt": prompt,
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
            "provider": provider,
        }
        result = await self.router.run(req)
        if "error" in result:
            raise RuntimeError(f"LLM call failed: {result['error']}")
        return result.get("output", "")
