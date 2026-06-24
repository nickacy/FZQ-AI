# tests/test_e2e/test_full_pipeline.py

import pytest
from fzq_ai.llm.router_v2.router import RouterV2
from fzq_ai.llm.orchestrator.orchestrator import MultiModelOrchestrator
from tests.utils.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_full_pipeline():
    router = RouterV2()
    orchestrator = MultiModelOrchestrator(strategy=None)

    orchestrator.strategy = lambda task: MockProvider()

    task = {
        "task_type": "zh_multisource_merge",
        "input": "中国经济最新动态"
    }

    result = await orchestrator.run(task)

    assert "output" in result
