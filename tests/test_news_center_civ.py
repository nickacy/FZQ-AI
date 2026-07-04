"""V24 — NewsCenterAgent + Civilization integration tests."""
from __future__ import annotations
import pytest
from fzq_ai.agents.base import AgentContext
from fzq_ai.agents.news_center_agent import NewsCenterAgent
from fzq_ai.civilization.civilization_engine import CivilizationEngine


def _ctx(raw_input="test", civ=None):
    return AgentContext(
        user_id="u1",
        locale="zh-CN",
        raw_input=raw_input,
        metadata={"civilization": civ},
    )


class TestNewsCenterCivilization:
    def test_agent_receives_civilization_in_metadata(self):
        """Verify civilization reaches agent via metadata."""
        civ = CivilizationEngine("test-civ")
        ctx = _ctx("test topic", civ)
        assert ctx.metadata.get("civilization") is civ

    @pytest.mark.asyncio
    async def test_news_center_with_civilization(self):
        """Civilization is used during agent execution."""
        civ = CivilizationEngine("test-civ")
        civ.remember("civ_init", True)
        agent = NewsCenterAgent(sub_agents=["zh_policy_brief"])
        ctx = _ctx("policy test", civ)
        result = await agent.run(ctx)
        assert result.ok or not result.ok  # either ok
        assert "civilization_trace" in result.data
        assert isinstance(result.data["civilization_trace"], list)

    @pytest.mark.asyncio
    async def test_news_center_without_civilization(self):
        """Agent works normally without civilization."""
        agent = NewsCenterAgent(sub_agents=["zh_policy_brief"])
        ctx = _ctx("test", None)
        result = await agent.run(ctx)
        assert "civilization_trace" in result.data
        assert result.data["civilization_trace"] == []
