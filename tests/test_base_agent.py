"""V24 — BaseAgent default-behavior tests.

BaseAgent in V24 is no longer ABC; subclasses can override only `run` and
the 9 hook methods are pass-through / no-op by default. These tests
verify that contract.
"""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest

from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult


class _MinimalAgent(BaseAgent):
    """A subclass that overrides only `name` — should still be instantiable
    and use default run()/plan()/etc. implementations."""
    name = "minimal"


class _RunOnlyAgent(BaseAgent):
    name = "run_only"
    def run(self, ctx: AgentContext) -> AgentResult:
        return AgentResult(ok=True, data={"overridden": True}, warnings=[], trace=["custom"])


def _ctx() -> AgentContext:
    return AgentContext(
        user_id="u1", locale="zh-CN", focus_regions=[],
        languages=["zh"], raw_input="x", metadata={},
    )


class TestBaseAgentDefaults:
    def test_minimal_subclass_is_instantiable(self):
        """V24: no @abstractmethod enforcement — any BaseAgent subclass instantiates."""
        a = _MinimalAgent(name="m")
        assert a.name == "m"
        assert isinstance(a, BaseAgent)

    def test_default_run_executes_plan_execute_loop(self):
        a = _MinimalAgent(name="m")
        r = a.run(_ctx())
        # Default run() walks the plan→execute→reflect→heal pipeline
        assert r.ok
        # Default plan() returns raw_input + metadata; default execute() returns {}
        assert r.data == {}
        # Default evaluate() returns 1.0 → no reflect/heal/retry triggered
        assert "Step 1: Planning" in r.trace
        assert "Step 4: Evaluating result" in r.trace
        # 1.0 score means no reflect/heal/retry steps appear
        assert not any("Score too low" in t for t in r.trace)

    def test_default_plan_returns_ctx_snapshot(self):
        a = _MinimalAgent(name="m")
        plan = a.plan(_ctx())
        assert plan["raw_input"] == "x"
        assert plan["metadata"] == {}

    def test_default_evaluate_accepts_anything(self):
        a = _MinimalAgent(name="m")
        assert a.evaluate({"any": "thing"}) == 1.0

    def test_default_reflect_heal_pass_through(self):
        a = _MinimalAgent(name="m")
        r = {"x": 1}
        assert a.reflect(r) is r
        assert a.heal(r) is r

    def test_default_route_and_auto_select_return_empty(self):
        a = _MinimalAgent(name="m")
        assert a.route({}) == ""
        assert a.auto_select_model({}) == ""

    def test_subclass_run_override_takes_precedence(self):
        a = _RunOnlyAgent(name="r")
        r = a.run(_ctx())
        assert r.data == {"overridden": True}
        # The default "Step 1: Planning" trace should NOT appear since
        # the subclass replaced run() entirely.
        assert r.trace == ["custom"]

    def test_memory_helpers(self):
        a = _MinimalAgent(name="m")
        a.memory_write("k", "v")
        assert a.memory_read("k") == "v"
        assert a.memory_read("missing") is None
