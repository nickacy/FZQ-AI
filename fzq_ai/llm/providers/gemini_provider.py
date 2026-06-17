# fzq_ai/llm/providers/gemini_provider.py

from fzq_ai.schemas.llm import LLMRequestSchema


class GeminiProvider:
    """Mock Gemini provider for testing."""

    async def run(self, req: LLMRequestSchema) -> str:
        return f"[Gemini] {req.prompt}"
