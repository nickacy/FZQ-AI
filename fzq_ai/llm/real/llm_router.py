"""LLM Router with multi-provider routing, fallback chain, circuit breaker, and load balancing."""
import asyncio
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field

from fzq_ai.schemas.real import (
    LLMRequest,
    LLMResponse,
    ModelProvider,
    RouterConfig,
    ProviderConfig,
    FallbackRecord,
    PipelineMetrics,
)
from fzq_ai.llm.real.openai_client import OpenAIClient
from fzq_ai.llm.real.deepseek_client import DeepSeekClient
from fzq_ai.llm.real.gemini_client import GeminiClient


@dataclass
class _CircuitState:
    failures: int = 0
    last_failure: Optional[float] = None
    open: bool = False


@dataclass
class _ProviderWrapper:
    client: Any
    config: ProviderConfig
    circuit: _CircuitState = field(default_factory=_CircuitState)
    latency_history: List[int] = field(default_factory=list)
    last_used: float = 0.0


class LLMRouter:
    """Multi-provider LLM router with fallback, circuit breaker, and load balancing."""

    def __init__(self, config: RouterConfig):
        self.config = config
        self._providers: Dict[ModelProvider, _ProviderWrapper] = {}
        self._fallback_records: List[FallbackRecord] = []
        self._metrics = PipelineMetrics(pipeline_name="llm_router")
        self._lock = asyncio.Lock()
        self._rr_index = 0
        self._build_providers()

    def _build_providers(self) -> None:
        for pc in self.config.providers:
            if not pc.enabled:
                continue
            client = self._create_client(pc)
            if client:
                self._providers[pc.provider] = _ProviderWrapper(
                    client=client,
                    config=pc,
                )

    def _create_client(self, pc: ProviderConfig) -> Optional[Any]:
        if pc.provider == ModelProvider.OPENAI:
            if not pc.api_key:
                return None
            return OpenAIClient(
                api_key=pc.api_key,
                base_url=pc.base_url,
                default_model=pc.default_model,
                timeout_seconds=pc.timeout_seconds,
                max_retries=pc.max_retries,
                retry_backoff_base=pc.retry_backoff_base,
            )
        if pc.provider == ModelProvider.DEEPSEEK:
            if not pc.api_key:
                return None
            return DeepSeekClient(
                api_key=pc.api_key,
                base_url=pc.base_url or "https://api.deepseek.com",
                default_model=pc.default_model,
                timeout_seconds=pc.timeout_seconds,
                max_retries=pc.max_retries,
                retry_backoff_base=pc.retry_backoff_base,
            )
        if pc.provider == ModelProvider.GEMINI:
            if not pc.api_key:
                return None
            return GeminiClient(
                api_key=pc.api_key,
                base_url=pc.base_url or "https://generativelanguage.googleapis.com/v1beta",
                default_model=pc.default_model,
                timeout_seconds=pc.timeout_seconds,
                max_retries=pc.max_retries,
                retry_backoff_base=pc.retry_backoff_base,
            )
        return None

    def _is_circuit_open(self, wrapper: _ProviderWrapper) -> bool:
        if not wrapper.circuit.open:
            return False
        if wrapper.circuit.last_failure is None:
            return False
        elapsed = time.time() - wrapper.circuit.last_failure
        return elapsed < self.config.circuit_breaker_timeout_seconds

    def _record_failure(self, wrapper: _ProviderWrapper) -> None:
        wrapper.circuit.failures += 1
        wrapper.circuit.last_failure = time.time()
        if wrapper.circuit.failures >= self.config.circuit_breaker_threshold:
            wrapper.circuit.open = True

    def _record_success(self, wrapper: _ProviderWrapper) -> None:
        wrapper.circuit.failures = 0
        wrapper.circuit.open = False
        wrapper.circuit.last_failure = None

    def _select_provider(self) -> Optional[ModelProvider]:
        available = [
            p for p, w in self._providers.items()
            if not self._is_circuit_open(w)
        ]
        if not available:
            return None

        strategy = self.config.load_balancing_strategy
        if strategy == "priority":
            available.sort(key=lambda p: self._providers[p].config.priority)
            return available[0]
        if strategy == "round_robin":
            for _ in range(len(available)):
                idx = self._rr_index % len(available)
                self._rr_index += 1
                candidate = available[idx]
                if not self._is_circuit_open(self._providers[candidate]):
                    return candidate
            return available[0]
        if strategy == "least_latency":
            def avg_latency(p: ModelProvider) -> float:
                hist = self._providers[p].latency_history
                if not hist:
                    return 0.0
                return sum(hist) / len(hist)
            available.sort(key=avg_latency)
            return available[0]

        return available[0]

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Route a request to the best available provider with fallback."""
        fallback_chain = [request.provider] + [
            p for p in self.config.fallback_chain if p != request.provider
        ]
        start = time.perf_counter()
        for provider in fallback_chain:
            wrapper = self._providers.get(provider)
            if wrapper is None or self._is_circuit_open(wrapper):
                continue
            try:
                resp = await wrapper.client.generate(request)
                latency_ms = int((time.perf_counter() - start) * 1000)
                if resp.error:
                    self._record_failure(wrapper)
                    self._fallback_records.append(
                        FallbackRecord(
                            original_provider=self.config.default_provider,
                            fallback_provider=provider,
                            reason=resp.error,
                            latency_ms=latency_ms,
                            success=False,
                        )
                    )
                    continue
                wrapper.latency_history.append(resp.latency_ms)
                wrapper.last_used = time.time()
                self._record_success(wrapper)
                if provider != request.provider:
                    self._metrics.fallback_count += 1
                self._metrics.model_usage[provider.value] = self._metrics.model_usage.get(provider.value, 0) + 1
                return resp
            except Exception as exc:
                self._record_failure(wrapper)
                self._fallback_records.append(
                    FallbackRecord(
                        original_provider=self.config.default_provider,
                        fallback_provider=provider,
                        reason=str(exc),
                        latency_ms=int((time.perf_counter() - start) * 1000),
                        success=False,
                    )
                )

        latency_ms = int((time.perf_counter() - start) * 1000)
        return LLMResponse(
            content="",
            provider=ModelProvider.OPENAI,
            model="fallback-failed",
            usage={},
            latency_ms=latency_ms,
            error="All providers failed",
        )

    async def health_check(self, provider: Optional[ModelProvider] = None) -> Dict[ModelProvider, bool]:
        """Run health checks for all or a specific provider."""
        targets = [provider] if provider else list(self._providers.keys())
        results: Dict[ModelProvider, bool] = {}
        for p in targets:
            wrapper = self._providers.get(p)
            if wrapper is None:
                results[p] = False
                continue
            try:
                ok = await wrapper.client.health_check()
                results[p] = ok
                if ok:
                    self._record_success(wrapper)
                else:
                    self._record_failure(wrapper)
            except Exception:
                results[p] = False
                self._record_failure(wrapper)
        return results

    async def run_health_checks(self) -> None:
        """Periodic health check task."""
        while True:
            await asyncio.sleep(self.config.health_check_interval_seconds)
            await self.health_check()

    def get_metrics(self) -> PipelineMetrics:
        """Return current router metrics."""
        return self._metrics

    def get_fallback_records(self) -> List[FallbackRecord]:
        """Return recorded fallback attempts."""
        return list(self._fallback_records)
