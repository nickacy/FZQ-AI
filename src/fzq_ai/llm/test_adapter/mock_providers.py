"""Mock LLM providers with the same interface as real clients. No API calls."""
from typing import Optional

from fzq_ai.schemas.test_adapter import LLMRequest, LLMResponse, ModelProvider


class MockOpenAIClient:
    """Mock OpenAI client. Returns fixed mock data. No API calls."""

    def __init__(
        self,
        api_key: str = "mock",
        base_url: Optional[str] = None,
        default_model: str = "mock-gpt",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
    ):
        self.provider = ModelProvider.OPENAI
        self.default_model = default_model

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Return a fixed mock response."""
        return LLMResponse(
            content=f"Mock OpenAI response: {request.prompt[:30]}...",
            provider=self.provider,
            model=request.model or self.default_model,
            usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            latency_ms=1,
            finish_reason="stop",
        )

    async def health_check(self) -> bool:
        """Always return healthy."""
        return True


class MockDeepSeekClient:
    """Mock DeepSeek client. Returns fixed mock data. No API calls."""

    def __init__(
        self,
        api_key: str = "mock",
        base_url: str = "https://mock.deepseek.com",
        default_model: str = "mock-deepseek",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
    ):
        self.provider = ModelProvider.DEEPSEEK
        self.default_model = default_model

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Return a fixed mock response."""
        return LLMResponse(
            content=f"Mock DeepSeek response: {request.prompt[:30]}...",
            provider=self.provider,
            model=request.model or self.default_model,
            usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            latency_ms=1,
            finish_reason="stop",
        )

    async def health_check(self) -> bool:
        """Always return healthy."""
        return True


class MockGeminiClient:
    """Mock Gemini client. Returns fixed mock data. No API calls."""

    def __init__(
        self,
        api_key: str = "mock",
        base_url: str = "https://mock.gemini.com",
        default_model: str = "mock-gemini",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
    ):
        self.provider = ModelProvider.GEMINI
        self.default_model = default_model

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Return a fixed mock response."""
        return LLMResponse(
            content=f"Mock Gemini response: {request.prompt[:30]}...",
            provider=self.provider,
            model=request.model or self.default_model,
            usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            latency_ms=1,
            finish_reason="stop",
        )

    async def health_check(self) -> bool:
        """Always return healthy."""
        return True
