from fzq_ai.schemas.llm import LLMRequestSchema

class OpenAIProvider:
    """Mock OpenAI provider for testing."""
    async def run(self, req: LLMRequestSchema) -> str:
        return f"[OpenAI] {req.prompt}"
