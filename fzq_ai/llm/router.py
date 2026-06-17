# fzq_ai/llm/router.py

from typing import Any
from fzq_ai.llm.providers import ProviderRegistry
from fzq_ai.llm.task_registry import TaskRegistry
from fzq_ai.schemas.llm import LLMRequestSchema, LLMResponseSchema


class LLMRouter:
    """Route LLM calls to the correct provider based on task type."""

    def __init__(self) -> None:
        self.task_registry = TaskRegistry()
        self.provider_registry = ProviderRegistry()

    async def route_llm_call(self, task_type: str, req: LLMRequestSchema) -> LLMResponseSchema:
        """Route the request to the correct provider/model."""
        task_cfg = self.task_registry.get(task_type)

        # Try primary model first
        try:
            provider = self.provider_registry.get_provider(task_cfg.primary_model)
            result = await provider.run(req)
            return LLMResponseSchema(content=result)
        except Exception:
            pass

        # Try fallback models
        for model in task_cfg.fallback_models:
            try:
                provider = self.provider_registry.get_provider(model)
                result = await provider.run(req)
                return LLMResponseSchema(content=result)
            except Exception:
                continue

        raise RuntimeError(f"All providers failed for task: {task_type}")
