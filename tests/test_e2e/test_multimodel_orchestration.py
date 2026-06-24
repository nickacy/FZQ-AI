# tests/test_e2e/test_orchestrator.py

import pytest
from fzq_ai.llm.orchestrator.orchestrator import MultiModelOrchestrator
from tests.utils.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_orchestrator_basic():
    orchestrator = MultiModelOrchestrator(strategy=None)
    orchestrator.strategy = lambda task: MockProvider()

    result = await orchestrator.run({"input": "测试"})

    assert "output" in result
    assert "audit" in result
