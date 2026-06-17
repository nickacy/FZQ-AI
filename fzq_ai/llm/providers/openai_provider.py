# fzq_ai/llm/providers/openai_provider.py

from fzq_ai.schemas.llm import LLMRequestSchema


class OpenAIProvider:
    """Mock OpenAI provider for testing."""

    async def run(self, req: LLMRequestSchema) -> str:
        # 在 Phase 4，我们只需要一个可运行的 mock
        return f"[OpenAI] {req.prompt}"
