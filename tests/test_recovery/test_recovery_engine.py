# tests/test_recovery/test_recovery_engine.py

import pytest
from fzq_ai.llm.orchestrator.recovery.recovery_engine import ErrorRecoveryEngine
from tests.utils.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_recovery_json_error():
    engine = ErrorRecoveryEngine()
    provider = MockProvider()

    result = await engine.recover(provider, {}, "{bad json", None)

    assert "output" in result
    assert "report" in result
