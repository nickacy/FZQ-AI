"""tests/test_formatter.py — Formatter 测试"""
import pytest
from fzq_ai.utils.formatter import NewsFormatter, NarrativeFormatter, RiskFormatter, DailyReportFormatter


class TestNewsFormatter:
    def test_format(self):
        raw = "Breaking news today"
        result = NewsFormatter.format(raw)
        assert "### 📰 新闻摘要" in result
        assert "Breaking news today" in result

    def test_format_strips_whitespace(self):
        raw = "  spaced  "
        result = NewsFormatter.format(raw)
        assert "spaced" in result


class TestNarrativeFormatter:
    def test_format(self):
        raw = "Narrative analysis text"
        result = NarrativeFormatter.format(raw)
        assert "### 📚 叙事分析" in result
        assert "Narrative analysis text" in result


class TestRiskFormatter:
    def test_format_valid_json(self):
        raw = '{"level": "high", "score": 0.8}'
        result = RiskFormatter.format(raw)
        assert isinstance(result, dict)
        assert result["level"] == "high"

    def test_format_invalid_json(self):
        raw = "not json"
        result = RiskFormatter.format(raw)
        assert isinstance(result, dict)
        assert "summary" in result
        assert "raw" in result


class TestDailyReportFormatter:
    def test_format(self):
        news = "News summary"
        narrative = {"key": "value"}
        risk = {"level": "medium"}
        result = DailyReportFormatter.format(news, narrative, risk)
        assert "# 📅 每日简报（Daily Report）" in result
        assert "News summary" in result
        assert "key" in result
        assert "medium" in result

    def test_format_with_string_inputs(self):
        result = DailyReportFormatter.format("n", "nar", "risk")
        assert "n" in result
        assert "nar" in result
        assert "risk" in result

    def test_format_includes_footer(self):
        result = DailyReportFormatter.format("a", "b", "c")
        assert "FZQ-AI Agent" in result

    def test_format_markdown_headers(self):
        result = DailyReportFormatter.format("a", "b", "c")
        assert "## 📰 新闻摘要" in result
        assert "## 📚 叙事分析" in result
        assert "## ⚠️ 风险扫描" in result

    def test_format_returns_string(self):
        result = DailyReportFormatter.format("a", "b", "c")
        assert isinstance(result, str)
