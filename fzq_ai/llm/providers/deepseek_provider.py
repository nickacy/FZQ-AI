from fzq_ai.schemas.llm import LLMRequestSchema

class DeepSeekProvider:
    """Mock DeepSeek provider for testing."""
    async def run(self, req: LLMRequestSchema) -> str:
        return f"[DeepSeek] {req.prompt}"
