# tools/runtime_health_check_v13.py
import asyncio
import traceback

from fzq_ai.pipelines.registry import PipelineRegistry, create_pipeline
from fzq_ai.llm.router import LLMRouter


# ---------- 1. Registry 快照 ----------
def check_registry_snapshot():
    print("\n[REGISTRY] Snapshot")
    try:
        families = PipelineRegistry.list_families()
        print("  families:", families)
        for fam in families:
            info = PipelineRegistry.get_family_info(fam)
            print(f"  - {fam}: versions={info['versions']}, default={info['default']}")
    except Exception:
        print("  -> ERROR in registry snapshot:")
        traceback.print_exc()


# ---------- 2. Router / Provider 路由检查 ----------
async def check_router_providers():
    print("\n[ROUTER] LLMRouter basic routing")

    router = LLMRouter()

    # 2.1 默认路由（不指定 provider）
    try:
        out = await router.route(
            "test_default",
            "用一句话总结：FZQ-AI 是什么？（测试默认路由）",
        )
        print("  [default] OK, len(output) =", len(str(out)))
    except Exception:
        print("  [default] ERROR:")
        traceback.print_exc()

    # 2.2 指定 provider = glm（或 glm-5.2，看你 Provider 注册名）
    try:
        req = {
            "task_type": "test_glm",
            "prompt": "用一句话总结：GLM-5.2 在本项目中的角色。（测试指定 provider）",
            "provider": "glm",  # 如果你注册的是 "glm-5.2"，这里改成 "glm-5.2"
        }
        out = await router.call(req)
        print("  [glm] OK, len(output) =", len(str(out)))
    except Exception:
        print("  [glm] ERROR:")
        traceback.print_exc()


# ---------- 3. 英文 Pipeline 运行检查 ----------
async def check_english_pipeline():
    print("\n[PIPELINE] English pipeline sanity check")

    try:
        # 这里假设你有一个 family 名为 "news" 或类似
        # 如果你的注册名不同，可以改成具体的，比如 "news_v1"
        NewsPipelineCls = PipelineRegistry.get("news@default")
        pipeline = NewsPipelineCls()

        if hasattr(pipeline, "run_async"):
            out = await pipeline.run_async(
                query="South China Sea tensions test query",
            )
        else:
            out = pipeline.run(query="South China Sea tensions test query")

        print("  [news] OK, type:", type(out))
    except Exception:
        print("  [news] ERROR:")
        traceback.print_exc()


# ---------- 4. 中文 Pipeline 运行检查（走 Router 的那一类，如果有） ----------
async def check_chinese_router_pipeline():
    print("\n[PIPELINE] Chinese router-based pipeline sanity check")

    # 如果你有走 Router 的中文 Pipeline，可以在这里补一条
    # 否则可以暂时跳过或改成任意一个你想测的 Pipeline
    try:
        # 示例：假设有 family "zh_news"
        # ZhNewsPipelineCls = PipelineRegistry.get("zh_news@default")
        # pipeline = ZhNewsPipelineCls()
        # out = await pipeline.run_async(query="测试中文新闻分析")
        # print("  [zh_news] OK, type:", type(out))
        print("  [zh_router] SKIP (no router-based zh pipeline configured in this script)")
    except Exception:
        print("  [zh_router] ERROR:")
        traceback.print_exc()


async def main():
    print("=== FZQ-AI v13 Runtime Health Check ===")

    # 1. Registry
    check_registry_snapshot()

    # 2. Router / Provider
    await check_router_providers()

    # 3. Pipelines
    await check_english_pipeline()
    await check_chinese_router_pipeline()

    print("\n=== Health Check Finished ===")


if __name__ == "__main__":
    asyncio.run(main())
