from fzq_ai.llm.orchestrator.orchestrator import MultiModelOrchestrator
from fzq_ai.llm.router_v2.router import RouterV2

def test_full_pipeline():
    router = RouterV2()
    orchestrator = MultiModelOrchestrator(strategy=None)

    task = {
        "task_type": "zh_multisource_merge",
        "input": "中国经济最新动态"
    }

    provider = router.select(task)
    result = orchestrator.run(task)

    assert "output" in result
