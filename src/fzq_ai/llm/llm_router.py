# fzq_ai/llm/llm_router.py

from typing import Any

from fzq_ai.llm.providers import ProviderRegistry
from fzq_ai.llm.task_registry import TaskRegistry
from fzq_ai.schemas.llm import LLMRequestSchema, LLMResponseSchema


class LLMRouter:
    """
    Real LLM router for production pipelines.

    - Uses TaskRegistry to decide primary and fallback models per task_type
    - Uses ProviderRegistry to get concrete provider instances
    - Exposes a simple async `route(task_type, prompt)` API for pipelines
    """

    def __init__(self) -> None:
        self.task_registry = TaskRegistry()
        self.provider_registry = ProviderRegistry()

    async def _route_llm_call(
        self,
        task_type: str,
        req: LLMRequestSchema,
    ) -> LLMResponseSchema:
        """
        Core routing logic: try primary model, then fallbacks.
        Returns a structured LLMResponseSchema.
        """
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

    async def route(self, task_type: str, prompt: str, **extra: Any) -> str:
        """
        Public API used by pipelines.

        - task_type: logical task name (e.g. 'news_intel', 'risk_summary')
        - prompt: final prompt string sent to the model
        - extra: optional extra fields for LLMRequestSchema (e.g. temperature)

        Returns:
            Plain string content from the LLM response.
        """
        req = LLMRequestSchema(
            task_type=task_type,
            prompt=prompt,
            **extra,
        )
        resp = await self._route_llm_call(task_type, req)
        return resp.content
