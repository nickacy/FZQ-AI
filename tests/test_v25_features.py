""
FZQ-AI v2.5 — Orchestrator / API / LLM Router 功能测试
运行: python -m pytest tests/test_v25_features.py -v
""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ── TaskOrchestrator 测试 ─────────────────────────────────────

class TestOrchestrator:

    def test_list_pipelines(self):
        from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
        orch = TaskOrchestrator()
        pipelines = orch.list_pipelines()
        assert isinstance(pipelines, dict)
        assert "news-intel" in pipelines
        assert "narrative" in pipelines
        assert "risk" in pipelines

    def test_run_nl_known_task(self):
        from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
        orch = TaskOrchestrator()
        result = orch.run_nl("news analysis", items=["topic"])
        assert isinstance(result, dict)
        assert "success" in result or "pipeline" in result or "error" in result

    def test_run_nl_chinese_keyword(self):
        from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
        orch = TaskOrchestrator()
        result = orch.run_nl("新闻分析", items=["全球要闻"])
        assert isinstance(result, dict)
        assert "pipeline" in result
        assert result["pipeline"] == "news-intel"

    def test_run_nl_unknown_task(self):
        from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
        orch = TaskOrchestrator()
        result = orch.run_nl("completely unknown task type", items=[])
        assert isinstance(result, dict)
        assert result.get("success") is False or "error" in result

    def test_run_nl_diagnostics(self):
        from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
        orch = TaskOrchestrator()
        result = orch.run_nl("risk scan", items=[])
        assert isinstance(result, dict)
        if "pipeline" in result:
            assert isinstance(result["pipeline"], str)


# ── LLM Router 测试 ───────────────────────────────────────────

class TestLLMRouter:

    def test_check_availability(self):
        with patch.dict(os.environ, {
            "DEEPSEEK_API_KEY": "sk-test",
            "OPENAI_API_KEY": "sk-test",
            "GEMINI_API_KEY": "sk-test",
        }):
            from fzq_ai.llm.llm_router import LLMRouter
            try:
                router = LLMRouter()
                status = router.check_availability()
                assert isinstance(status, dict)
                for name in ["deepseek", "openai", "gemini"]:
                    assert name in status
                    assert isinstance(status[name], bool)
            except (ValueError, RuntimeError):
                pytest.skip("Router init requires valid API keys")

    def test_provider_state_defaults(self):
        from fzq_ai.llm.llm_router import ProviderState
        state = ProviderState("test")
        assert state.healthy is True
        assert state.consecutive_failures == 0
        assert state.total_calls == 0

    def test_provider_state_failure_tracking(self):
        from fzq_ai.llm.llm_router import ProviderState
        state = ProviderState("test")
        state.record_failure()
        state.record_failure()
        assert state.total_calls == 2
        assert state.consecutive_failures == 2
        assert state.healthy is True  # Not yet 3
        state.record_failure()
        assert state.consecutive_failures == 3
        assert state.healthy is False
        state.record_success()
        assert state.consecutive_failures == 0
        assert state.healthy is True

