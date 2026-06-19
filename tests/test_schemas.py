"""tests/test_schemas.py — Schema 模型测试"""
import pytest
from datetime import datetime, timezone
from fzq_ai.schemas.test_adapter import (
    LanguageCode, RegionCode, AnalysisDimension, RiskLevel, SentimentLabel, ModelProvider,
    NewsSource, RawNewsItem, TranslatedNewsItem, NarrativeAnalysis, RiskFactor, RiskAnalysis,
    SentimentAnalysis, ScenarioProjection, ScenarioAnalysis, MultiDimensionAnalysis,
    DailyReportSection, DailyReport, LLMRequest, LLMResponse, PipelineInput, PipelineOutput,
    PipelineMetrics, PromptTemplate, ProviderConfig, RouterConfig, FallbackRecord,
)


class TestEnums:
    def test_language_code(self):
        assert LanguageCode.EN == "en"
        assert LanguageCode.ZH == "zh"

    def test_region_code(self):
        assert RegionCode.US == "us"
        assert RegionCode.CN == "cn"
        assert RegionCode.GLOBAL == "global"

    def test_analysis_dimension(self):
        assert AnalysisDimension.NARRATIVE == "narrative"
        assert AnalysisDimension.RISK == "risk"
        assert AnalysisDimension.SENTIMENT == "sentiment"
        assert AnalysisDimension.SCENARIO == "scenario"

    def test_risk_level(self):
        assert RiskLevel.CRITICAL == "critical"
        assert RiskLevel.MINIMAL == "minimal"

    def test_sentiment_label(self):
        assert SentimentLabel.VERY_POSITIVE == "very_positive"
        assert SentimentLabel.VERY_NEGATIVE == "very_negative"

    def test_model_provider(self):
        assert ModelProvider.OPENAI == "openai"
        assert ModelProvider.GEMINI == "gemini"
        assert ModelProvider.DEEPSEEK == "deepseek"

    def test_all_enum_values_unique(self):
        assert len(set(LanguageCode)) == len(LanguageCode)
        assert len(set(RegionCode)) == len(RegionCode)
        assert len(set(AnalysisDimension)) == len(AnalysisDimension)
        assert len(set(RiskLevel)) == len(RiskLevel)
        assert len(set(SentimentLabel)) == len(SentimentLabel)
        assert len(set(ModelProvider)) == len(ModelProvider)


class TestNewsSchemas:
    def test_news_source(self):
        s = NewsSource(name="BBC", region=RegionCode.UK, reliability_score=0.95)
        assert s.name == "BBC"
        assert s.reliability_score == 0.95

    def test_raw_news_item(self):
        s = NewsSource(name="Test")
        item = RawNewsItem(
            id="n1", title="T", content="C", source=s,
            published_at=datetime.now(timezone.utc), language=LanguageCode.EN, region=RegionCode.US,
        )
        assert item.id == "n1"
        assert item.language == LanguageCode.EN

    def test_translated_news_item(self):
        s = NewsSource(name="Test")
        original = RawNewsItem(
            id="n1", title="T", content="C", source=s,
            published_at=datetime.now(timezone.utc), language=LanguageCode.ZH, region=RegionCode.CN,
        )
        translated = TranslatedNewsItem(
            original=original, translated_title="Trans", translated_content="Trans C",
            target_language=LanguageCode.EN, translation_confidence=0.95,
        )
        assert translated.translation_confidence == 0.95
        assert translated.target_language == LanguageCode.EN


class TestAnalysisSchemas:
    def test_narrative_analysis(self):
        na = NarrativeAnalysis(news_id="n1", primary_narrative="Test", narrative_strength=0.8)
        assert na.primary_narrative == "Test"
        assert na.narrative_strength == 0.8

    def test_risk_factor(self):
        rf = RiskFactor(risk_type="market", level=RiskLevel.HIGH, probability=0.7)
        assert rf.risk_type == "market"
        assert rf.level == RiskLevel.HIGH

    def test_risk_analysis(self):
        ra = RiskAnalysis(news_id="n1", overall_risk_level=RiskLevel.HIGH, composite_risk_score=0.7)
        assert ra.composite_risk_score == 0.7

    def test_sentiment_analysis(self):
        sa = SentimentAnalysis(news_id="n1", overall_sentiment=SentimentLabel.POSITIVE, sentiment_score=0.6)
        assert sa.sentiment_score == 0.6

    def test_scenario_projection(self):
        sp = ScenarioProjection(scenario_name="Base", probability=0.5, time_horizon="short")
        assert sp.scenario_name == "Base"

    def test_scenario_analysis(self):
        sa = ScenarioAnalysis(news_id="n1")
        assert sa.base_case is not None

    def test_multi_dimension_analysis(self):
        mda = MultiDimensionAnalysis(news_id="n1", aggregated_priority_score=0.75)
        assert mda.aggregated_priority_score == 0.75
        assert mda.narrative is not None


class TestReportSchemas:
    def test_daily_report_section(self):
        sec = DailyReportSection(section_title="S", section_type="overview", content="C")
        assert sec.priority == 5

    def test_daily_report(self):
        dr = DailyReport(report_id="r1", report_date=datetime.now(timezone.utc))
        assert dr.report_id == "r1"
        assert dr.language == LanguageCode.EN


class TestLLMSchemas:
    def test_llm_request(self):
        req = LLMRequest(prompt="test", model="gpt-4", temperature=0.5)
        assert req.prompt == "test"
        assert req.temperature == 0.5

    def test_llm_response(self):
        resp = LLMResponse(content="ok", provider=ModelProvider.OPENAI, model="gpt-4", latency_ms=100)
        assert resp.content == "ok"
        assert resp.latency_ms == 100

    def test_fallback_record(self):
        fr = FallbackRecord(original_provider=ModelProvider.OPENAI, fallback_provider=ModelProvider.GEMINI, reason="test")
        assert fr.reason == "test"
        assert fr.success is True

    def test_prompt_template(self):
        pt = PromptTemplate(name="t", template="{{x}}", variables=["x"])
        assert pt.name == "t"
        assert "x" in pt.variables

    def test_provider_config(self):
        pc = ProviderConfig(provider=ModelProvider.DEEPSEEK, default_model="ds-v3")
        assert pc.default_model == "ds-v3"

    def test_router_config(self):
        rc = RouterConfig()
        assert rc.load_balancing_strategy == "priority"
        assert rc.metrics_enabled is True

    def test_pipeline_metrics(self):
        pm = PipelineMetrics(pipeline_name="test", items_processed=10, avg_latency_ms=50.0)
        assert pm.items_processed == 10

    def test_pipeline_input(self):
        pi = PipelineInput(max_items=50, priority_threshold=0.3)
        assert pi.max_items == 50
        assert pi.priority_threshold == 0.3

    def test_pipeline_output(self):
        pi = PipelineInput()
        pm = PipelineMetrics(pipeline_name="test")
        po = PipelineOutput(input_summary=pi, metrics=pm)
        assert po.analyzed_items == []
