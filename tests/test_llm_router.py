"""tests/test_llm_router.py — LLM Router 测试"""
import pytest
from fzq_ai.schemas.test_adapter import LLMRequest, LLMResponse, ModelProvider, RouterConfig
from fzq_ai.llm.test_adapter import MockLLMRouter, MockOpenAIClient, MockDeepSeekClient, MockGeminiClient


class TestMockLLMRouter:
    @pytest.mark.asyncio
    async def test_generate_returns_llm_response(self):
        router = MockLLMRouter(config=RouterConfig())
        req = LLMRequest(prompt="Test prompt", provider=ModelProvider.OPENAI)
        resp = await router.generate(req)
        assert isinstance(resp, LLMResponse)
        assert resp.latency_ms == 1
        assert resp.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_tracks_metrics(self):
        router = MockLLMRouter(config=RouterConfig())
        req = LLMRequest(prompt="Test", provider=ModelProvider.OPENAI)
        await router.generate(req)
        await router.generate(req)
        metrics = router.get_metrics()
        assert metrics.model_usage.get(ModelProvider.OPENAI.value, 0) >= 1

    @pytest.mark.asyncio
    async def test_health_check_all_providers(self):
        router = MockLLMRouter(config=RouterConfig())
        health = await router.health_check()
        assert isinstance(health, dict)
        for p in RouterConfig().fallback_chain:
            assert health.get(p, False) is True

    @pytest.mark.asyncio
    async def test_health_check_single_provider(self):
        router = MockLLMRouter(config=RouterConfig())
        health = await router.health_check(ModelProvider.DEEPSEEK)
        assert health[ModelProvider.DEEPSEEK] is True

    def test_get_fallback_records(self):
        router = MockLLMRouter(config=RouterConfig())
        records = router.get_fallback_records()
        assert isinstance(records, list)

    def test_get_metrics_returns_pipeline_metrics(self):
        router = MockLLMRouter(config=RouterConfig())
        metrics = router.get_metrics()
        assert metrics.pipeline_name == "mock_llm_router"


class TestMockProviders:
    @pytest.mark.asyncio
    async def test_mock_openai_client_generate(self):
        client = MockOpenAIClient()
        req = LLMRequest(prompt="Hello")
        resp = await client.generate(req)
        assert isinstance(resp, LLMResponse)
        assert resp.provider == ModelProvider.OPENAI
        assert resp.latency_ms == 1

    @pytest.mark.asyncio
    async def test_mock_openai_client_health_check(self):
        client = MockOpenAIClient()
        assert await client.health_check() is True

    @pytest.mark.asyncio
    async def test_mock_deepseek_client_generate(self):
        client = MockDeepSeekClient()
        req = LLMRequest(prompt="Hello")
        resp = await client.generate(req)
        assert isinstance(resp, LLMResponse)
        assert resp.provider == ModelProvider.DEEPSEEK

    @pytest.mark.asyncio
    async def test_mock_gemini_client_generate(self):
        client = MockGeminiClient()
        req = LLMRequest(prompt="Hello")
        resp = await client.generate(req)
        assert isinstance(resp, LLMResponse)
        assert resp.provider == ModelProvider.GEMINI

    def test_mock_openai_client_properties(self):
        client = MockOpenAIClient()
        assert client.provider == ModelProvider.OPENAI
        assert client.default_model == "mock-gpt"

    def test_mock_deepseek_client_properties(self):
        client = MockDeepSeekClient()
        assert client.provider == ModelProvider.DEEPSEEK
        assert client.default_model == "mock-deepseek"

    def test_mock_gemini_client_properties(self):
        client = MockGeminiClient()
        assert client.provider == ModelProvider.GEMINI
        assert client.default_model == "mock-gemini"
