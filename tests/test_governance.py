"""QWEN Governance — registry health + fallback + trace tests."""

from __future__ import annotations
import pytest
from fzq_ai.registry.agents import (
    register_agent, get_agent, get_with_fallback,
    set_fallback, agent_health_report,
    AGENT_REGISTRY, AGENT_METADATA, AGENT_HEALTH, FALLBACK_CHAIN,
)


class DummyAgent:
    def __init__(self):
        self.name = "dummy"


class FailingAgent:
    def __init__(self):
        raise RuntimeError("intentional failure")


class TestAgentRegistryGovernance:
    def test_register_with_metadata(self):
        register_agent("test_dummy", DummyAgent, role="test", priority=9)
        assert "test_dummy" in AGENT_REGISTRY
        assert AGENT_METADATA["test_dummy"]["role"] == "test"
        assert AGENT_METADATA["test_dummy"]["priority"] == 9

    def test_health_initialized(self):
        register_agent("test_health", DummyAgent, role="test")
        assert AGENT_HEALTH["test_health"]["status"] == "ok"
        assert AGENT_HEALTH["test_health"]["failures"] == 0

    def test_get_agent_returns_fresh_instance(self):
        register_agent("test_instance", DummyAgent, role="test")
        a1 = get_agent("test_instance")
        a2 = get_agent("test_instance")
        assert a1 is not a2  # fresh each time

    def test_get_agent_none_for_missing(self):
        assert get_agent("nonexistent_agent_xyz") is None

    def test_get_with_fallback_uses_primary(self):
        register_agent("test_primary", DummyAgent, role="test")
        result = get_with_fallback("test_primary")
        assert result is not None

    def test_fallback_chain_works(self):
        register_agent("test_secondary", DummyAgent, role="test")
        set_fallback("test_nonexistent", "test_secondary")
        result = get_with_fallback("test_nonexistent")
        assert result is not None

    def test_health_report_structure(self):
        report = agent_health_report()
        assert "agents" in report
        assert "fallback_chain" in report
        assert isinstance(report["trace_count"], int)

    def test_instantiation_failure_handled(self):
        register_agent("test_failing", FailingAgent, role="test")
        AGENT_HEALTH["test_failing"]["failures"] = 0
        result = get_agent("test_failing")
        assert result is None
        assert AGENT_HEALTH["test_failing"]["failures"] >= 1

    def test_fallback_returns_none_when_both_missing(self):
        result = get_with_fallback("completely_missing_xyz")
        assert result is None
