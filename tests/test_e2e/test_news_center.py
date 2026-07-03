"""V24 — NewsCenterAgent integration tests.

Verifies the multi-agent aggregator behavior:
  - All 4 zh_tasks sub-agents are dispatched
  - Per-sub-agent failures are isolated (do not crash the aggregator)
  - Aggregator result is well-formed (ok, view_type, components, warnings, trace)
  - Custom sub_agent list is honored
  - Missing agents (not in registry) are reported as warnings, not raised
"""
from __future__ import annotations
import os

import pytest

# Make sure the package is importable when this file is run standalone
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fzq_ai.agents.base import AgentContext
from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.registry.agents import get_agent, AGENT_REGISTRY


def _ctx(raw_input: str = "test topic") -> AgentContext:
    return AgentContext(
        user_id="u1",
        locale="zh-CN",
        focus_regions=[],
        languages=["zh"],
        raw_input=raw_input,
        metadata={},
    )


class TestNewsCenterDispatch:
    def test_default_sub_agents_are_registered(self):
        """All 4 default sub-agents must be present in the registry."""
        for name in ("zh_policy_brief", "zh_risk_scan", "zh_opinion_landscape", "zh_multisource_merge"):
            assert name in AGENT_REGISTRY, f"{name} not registered"
            assert get_agent(name) is not None

    def test_aggregator_returns_all_4_components(self):
        news = get_agent("news_center")
        assert isinstance(news, NewsCenterAgent)
        result = news.run(_ctx("AI 监管"))

        # All 4 sub-agents should appear in components
        components = result.data["components"]
        assert set(components.keys()) == {
            "zh_policy_brief", "zh_risk_scan",
            "zh_opinion_landscape", "zh_multisource_merge",
        }

    def test_aggregator_view_shape(self):
        news = get_agent("news_center")
        result = news.run(_ctx("AI 监管"))
        # Top-level data must be well-formed
        assert result.data["view_type"] == "personal_intel_center"
        assert result.data["topic"] == "AI 监管"
        assert result.data["languages"] == ["zh"]
        assert isinstance(result.data["focus_regions"], list)

    def test_trace_records_per_subagent_step(self):
        news = get_agent("news_center")
        result = news.run(_ctx())
        # trace should start with news_center_start and have one entry per sub-agent
        assert result.trace[0] == "news_center_start"
        # 4 sub-agents → 4 _done or _error entries after the start
        sub_traces = [t for t in result.trace[1:] if t.endswith("_done") or t.endswith("_error")]
        assert len(sub_traces) == 4

    def test_isolates_per_subagent_failures(self):
        """A sub-agent that raises must NOT crash the aggregator."""
        # Custom aggregator that includes a non-existent agent
        agent = NewsCenterAgent(sub_agents=["not_a_real_agent"])
        result = agent.run(_ctx())
        assert result.ok is False  # at least one failure
        # The missing agent's failure is captured in warnings, not raised
        assert any("not_a_real_agent" in w for w in result.warnings)

    def test_partial_failure_yields_partial_data(self):
        """If only some sub-agents succeed, components still has all keys
        (with None for the failed ones)."""
        agent = NewsCenterAgent(sub_agents=["report", "not_a_real_agent"])
        result = agent.run(_ctx())
        assert "report" in result.data["components"]
        assert "not_a_real_agent" in result.data["components"]
        assert result.data["components"]["not_a_real_agent"] is None

    def test_warnings_collect_from_all_subagents(self):
        agent = NewsCenterAgent(sub_agents=["a", "b", "c"])
        result = agent.run(_ctx())
        # All 3 missing agents generate warnings
        missing_warnings = [w for w in result.warnings if "not registered" in w]
        assert len(missing_warnings) == 3

    def test_memory_keys_present_in_data(self):
        result = get_agent("news_center").run(_ctx("topic-xyz"))
        # topic is propagated to data
        assert result.data["topic"] == "topic-xyz"
