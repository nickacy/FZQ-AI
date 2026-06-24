# tests/test_e2e/test_full_pipeline.py

import pytest
from fzq_ai.llm.orchestrator.orchestrator import MultiModelOrchestrator
from tests.utils.mock_provider import MockProvider


class MockStrategy:
    """Mock strategy for testing."""
    def primary(self, task):
        return MockProvider()
    def validator(self, task):
        return MockProvider()
    def repair(self, task):
        return MockProvider()
    def audit(self, task):
        return MockProvider()


@pytest.mark.asyncio
async def test_full_pipeline():
    orchestrator = MultiModelOrchestrator(strategy=MockStrategy())

    task = {
        "task_type": "zh_multisource_merge",
        "input": "test input",
    }

    result = await orchestrator.run(task)

    assert "output" in result
