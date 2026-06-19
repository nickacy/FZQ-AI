"""tests/test_api.py — API 层基础测试"""
import pytest
from datetime import datetime, timezone
from fzq_ai.schemas.test_adapter import (
    LanguageCode,
    RegionCode,
    AnalysisDimension,
    RiskLevel,
    SentimentLabel,
    ModelProvider,
    NewsSource,
    RawNewsItem,
    NarrativeAnalysis,
    RiskAnalysis,
    RiskFactor,
    SentimentAnalysis,
    ScenarioAnalysis,
    ScenarioProjection,
    MultiDimensionAnalysis,
    DailyReport,
    DailyReportSection,
    LLMRequest,
    LLMResponse,
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    ProviderConfig,
    RouterConfig,
    FallbackRecord,
    PromptTemplate,
)
from fzq_ai.core.config import FZQConfig


class TestAPIImports:
    def test_all_schemas_importable(self):
        assert NewsSource(name="Test")
        assert RawNewsItem(
            id="t1",
            title="Title",
            content="Content",
            source=NewsSource(name="S"),
            published_at=datetime.now(timezone.utc),
            language=LanguageCode.EN,
            region=RegionCode.US,
        )
        assert NarrativeAnalysis(news_id="t1")
        assert RiskAnalysis(news_id="t1")
        assert RiskFactor()
        assert SentimentAnalysis(news_id="t1")
        assert ScenarioProjection()
        assert ScenarioAnalysis(news_id="t1")
        assert MultiDimensionAnalysis(news_id="t1")
        assert DailyReportSection()
        assert DailyReport(report_id="r1", report_date=datetime.now(timezone.utc))
        assert LLMRequest(prompt="test")
        assert LLMResponse(content="test", provider=ModelProvider.OPENAI, model="m", latency_ms=1)
        assert PipelineInput()
        assert PipelineOutput(input_summary=PipelineInput(), metrics=PipelineMetrics(pipeline_name="test"))
        assert ProviderConfig(provider=ModelProvider.OPENAI, default_model="gpt-4")
        assert RouterConfig()
        assert FallbackRecord()
        assert PromptTemplate(name="t", template="{{x}}")

    def test_config_from_env(self):
        config = FZQConfig.from_env()
        assert isinstance(config.test_mode, bool)
        assert isinstance(config.max_concurrent_llm_requests, int)

    def test_enum_values(self):
        assert LanguageCode.EN.value == "en"
        assert RegionCode.CN.value == "cn"
        assert AnalysisDimension.NARRATIVE.value == "narrative"
        assert RiskLevel.CRITICAL.value == "critical"
        assert SentimentLabel.POSITIVE.value == "positive"
        assert ModelProvider.DEEPSEEK.value == "deepseek"

    def test_enum_uniqueness(self):
        assert len(set(LanguageCode)) == len(LanguageCode)
        assert len(set(RegionCode)) == len(RegionCode)
        assert len(set(AnalysisDimension)) == len(AnalysisDimension)
        assert len(set(RiskLevel)) == len(RiskLevel)
        assert len(set(SentimentLabel)) == len(SentimentLabel)
        assert len(set(ModelProvider)) == len(ModelProvider)

    def test_raw_news_item_with_translation(self):
        source = NewsSource(name="BBC", region=RegionCode.UK, language=LanguageCode.EN)
        item = RawNewsItem(
            id="news_001",
            title="UK Election",
            content="Details...",
            source=source,
            published_at=datetime.now(timezone.utc),
            language=LanguageCode.EN,
            region=RegionCode.UK,
            translated_title="英国大选",
            translated_content="详情...",
            translation_confidence=0.92,
        )
        assert item.translated_title == "英国大选"
        assert item.translation_confidence == 0.92

    def test_pipeline_input_defaults(self):
        inp = PipelineInput()
        assert inp.target_language == LanguageCode.EN
        assert len(inp.dimensions) == 4
        assert inp.max_items == 100

    def test_router_config_defaults(self):
        cfg = RouterConfig()
        assert cfg.default_provider == ModelProvider.OPENAI
        assert len(cfg.fallback_chain) == 3
        assert cfg.circuit_breaker_threshold == 5

    def test_llm_request_defaults(self):
        req = LLMRequest(prompt="hello")
        assert req.provider == ModelProvider.OPENAI
        assert req.temperature == 0.3
        assert req.stream is False

    def test_daily_report_section_types(self):
        for st in ["overview", "highlight", "regional", "risk_alert", "sentiment_trend", "scenario_watch", "market_impact"]:
            sec = DailyReportSection(section_title="T", section_type=st, content="C")
            assert sec.section_type == st
