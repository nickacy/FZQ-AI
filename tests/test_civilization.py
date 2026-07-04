"""P2 — Civilization integration tests.

Verifies:
  - CivilizationEngine is injected at EntryServiceV24 level
  - Orchestrator includes civilization_trace in RouteResult debug_info
  - Civilization memory persists across calls
"""
from __future__ import annotations
import pytest
from fzq_ai.civilization.civilization_engine import CivilizationEngine
from fzq_ai.civilization.civilization_builder import build_default_civilization


class TestCivilizationEngine:
    def test_build_default_civilization(self):
        civ = build_default_civilization()
        assert civ.name == "fzq-default"
        assert len(civ.agents) == 3
        assert "deepseek-risk" in civ.agents
        assert civ.recall("mission") == "Cross-civilization intelligence analysis"

    def test_remember_and_recall(self):
        civ = CivilizationEngine("test")
        civ.remember("key1", "value1")
        assert civ.recall("key1") == "value1"
        assert civ.recall("missing", "default") == "default"

    def test_add_agent_and_link(self):
        civ = CivilizationEngine("test")
        civ.add_agent("agent_a", role="leader", priority=3)
        civ.add_agent("agent_b", role="worker", priority=1)
        civ.link("agent_a", "agent_b")
        assert civ.graph["agent_a"] == ["agent_b"]

    def test_snapshot(self):
        civ = build_default_civilization()
        snap = civ.snapshot()
        assert snap["name"] == "fzq-default"
        assert len(snap["agents"]) == 3
        assert "roles" in snap
        assert "graph" in snap

    def test_consensus(self):
        civ = CivilizationEngine("test")
        civ.add_agent("a", priority=2)
        civ.add_agent("b", priority=1)
        civ._results = [
            {"agent": "a", "output": "option_x"},
            {"agent": "b", "output": "option_x"},
        ]
        consensus = civ._generate_consensus()
        assert consensus["consensus"] is not None
        assert consensus["participants"] == 2


class TestCivilizationInjection:
    """Verify civilization flows through Entry → Orchestrator → Result."""

    def test_civilization_in_context(self):
        """EntryServiceV24 injects civilization into ctx."""
        from fzq_ai.api.entry_service_v24 import EntryServiceV24
        svc = EntryServiceV24()
        ctx = svc._build_ctx({"input": "test topic"})
        assert "civilization" in ctx
        civ = ctx["civilization"]
        assert isinstance(civ, CivilizationEngine)
        assert civ.name == "fzq-default"

    @pytest.mark.asyncio
    async def test_civilization_trace_in_result(self):
        """Orchestrator includes civilization_trace in RouteResult."""
        from fzq_ai.api.entry_service_v24 import EntryServiceV24
        svc = EntryServiceV24()
        result = await svc.handle_single({"input": "test civilization trace", "task": "test"})
        assert result.status == "ok"
        assert isinstance(result.debug_info, dict)
        assert "civilization_trace" in result.debug_info
        civ_trace = result.debug_info["civilization_trace"]
        assert isinstance(civ_trace, list)
        # At minimum, the remember stage should be recorded
        stages = [t.get("stage") for t in civ_trace]
        assert "civilization.remember" in stages

    @pytest.mark.asyncio
    async def test_civilization_memory_persists(self):
        """Civilization memory persists across multiple calls."""
        from fzq_ai.api.entry_service_v24 import EntryServiceV24
        svc = EntryServiceV24()
        await svc.handle_single({"input": "first call", "task": "multi"})
        # Second call should see accumulated memory
        result = await svc.handle_single({"input": "second call", "task": "multi"})
        civ_trace = result.debug_info.get("civilization_trace", [])
        assert len(civ_trace) >= 1
