"""Mock LLM router with the same interface as the real router. No real API calls."""
from typing import Any, Dict, List, Optional

from fzq_ai.schemas.test_adapter import (
    LLMRequest,
    LLMResponse,
    ModelProvider,
    RouterConfig,
    FallbackRecord,
    PipelineMetrics,
)


class MockLLMRouter:
    """Mock LLM router. Returns fixed LLMResponse with latency_ms=1. No concurrency, no health checks."""

    def __init__(self, config: RouterConfig):
        self.config = config
        self._metrics = PipelineMetrics(pipeline_name="mock_llm_router")
        self._fallback_records: List[FallbackRecord] = []

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Return a fixed mock response."""
        self._metrics.model_usage[request.provider.value] = self._metrics.model_usage.get(request.provider.value, 0) + 1
        return LLMResponse(
            content=f"Mock response for: {request.prompt[:50]}...",
            provider=request.provider,
            model=request.model or "mock-model",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            latency_ms=1,
            finish_reason="stop",
        )

    async def health_check(self, provider: Optional[ModelProvider] = None) -> Dict[ModelProvider, bool]:
        """Always return healthy for all providers."""
        targets = [provider] if provider else self.config.fallback_chain
        return {p: True for p in targets}

    def get_metrics(self) -> PipelineMetrics:
        """Return current mock metrics."""
        return self._metrics

    def get_fallback_records(self) -> List[FallbackRecord]:
        """Return empty fallback records."""
        return list(self._fallback_records)
