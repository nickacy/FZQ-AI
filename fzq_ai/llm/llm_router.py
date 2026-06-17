# fzq_ai/llm/llm_router.py

from fzq_ai.schemas.llm import LLMRequestSchema, LLMResponseSchema
from fzq_ai.llm.providers import ProviderRegistry


class LLMRouter:
    """Route LLM calls to the correct provider based on task type."""

    def __init__(self):
        self.registry = ProviderRegistry()

    async def route_llm_call(self, task_type: str, req: LLMRequestSchema) -> LLMResponseSchema:
        """Route the request to the correct provider."""
        # Phase 4 mock: always use primary provider "openai"
        provider = self.registry.get_provider("openai")
        result = await provider.run(req)
        return LLMResponseSchema(content=result)
