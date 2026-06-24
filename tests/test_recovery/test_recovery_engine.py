from fzq_ai.llm.orchestrator.recovery.recovery_engine import ErrorRecoveryEngine

def test_recovery_json_error():
    engine = ErrorRecoveryEngine()
    result = engine.recover(provider=None, task={}, raw_output="{bad json", error=None)
    assert "output" in result
