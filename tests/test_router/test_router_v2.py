from fzq_ai.llm.router_v2.router import RouterV2

def test_router_v2_select_merge():
    router = RouterV2()
    provider = router.select({"task_type": "zh_multisource_merge", "input": "xxx"})
    assert provider in ["glm-5.2", "qwen", "deepseek"]
