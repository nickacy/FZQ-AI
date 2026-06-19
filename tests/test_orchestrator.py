"""tests/test_orchestrator.py — Orchestrator 测试"""
import pytest
from fzq_ai.schemas.test_adapter import PipelineInput, DailyReport, LanguageCode, RegionCode
from fzq_ai.orchestrator.test_adapter import MockTaskOrchestrator


class TestMockTaskOrchestrator:
    def test_run_returns_daily_report(self):
        orch = MockTaskOrchestrator()
        inp = PipelineInput()
        report = orch.run(inp)
        assert isinstance(report, DailyReport)
        assert report.report_id is not None

    def test_run_has_sections(self):
        orch = MockTaskOrchestrator()
        report = orch.run(PipelineInput())
        assert len(report.sections) >= 1

    def test_run_has_top_stories(self):
        orch = MockTaskOrchestrator()
        report = orch.run(PipelineInput())
        assert len(report.top_stories) >= 1

    def test_run_daily(self):
        orch = MockTaskOrchestrator()
        report = orch.run_daily("global", ["news1", "news2"])
        assert isinstance(report, DailyReport)
        assert report.report_date is not None

    def test_schedule_daily(self):
        orch = MockTaskOrchestrator()
        orch.schedule_daily(callback=lambda r: None)
        orch.stop_schedule()

    def test_trigger_scheduled(self):
        orch = MockTaskOrchestrator()
        orch.schedule_daily(callback=lambda r: None)
        report = orch.trigger_scheduled()
        assert isinstance(report, DailyReport)

    def test_trigger_scheduled_no_callback(self):
        orch = MockTaskOrchestrator()
        result = orch.trigger_scheduled()
        assert result is None

    def test_run_with_region_filter(self):
        orch = MockTaskOrchestrator()
        inp = PipelineInput(region_filter=[RegionCode.CN])
        report = orch.run(inp)
        assert isinstance(report, DailyReport)

    def test_run_metadata(self):
        orch = MockTaskOrchestrator()
        report = orch.run(PipelineInput())
        assert report.metadata.get("mock") is True

    def test_run_generation_latency(self):
        orch = MockTaskOrchestrator()
        report = orch.run(PipelineInput())
        assert report.generation_latency_ms == 1

    def test_model_used(self):
        orch = MockTaskOrchestrator()
        report = orch.run(PipelineInput())
        from fzq_ai.schemas.test_adapter import ModelProvider
        assert report.model_used in ModelProvider
