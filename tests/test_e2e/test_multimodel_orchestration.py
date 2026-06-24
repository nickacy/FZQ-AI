# tests/test_e2e/test_orchestrator.py

import pytest
from fzq_ai.llm.orchestrator.orchestrator import MultiModelOrchestrator
from tests.utils.mock_provider import MockProvider


class MockStrategy:
    def primary(self, task):
        return MockProvider()
    def validator(self, task):
        return MockProvider()
    def repair(self, task):
        return MockProvider()
    def audit(self, task):
        return MockProvider()


@pytest.mark.asyncio
async def test_orchestrator_basic():
    orchestrator = MultiModelOrchestrator(strategy=MockStrategy())

    result = await orchestrator.run({"input": "test"})

    assert "output" in result
    assert "audit" in result
