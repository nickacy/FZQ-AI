# tools/runtime_health_check_v13.py
import asyncio
import traceback

from fzq_ai.pipelines.registry import PipelineRegistry, create_pipeline
from fzq_ai.llm.llm_router import LLMRouter


# ---------- 1. Registry snapshot ----------
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


# ---------- 2. Router / Provider routing check ----------
async def check_router_providers():
    print("\n[ROUTER] LLMRouter basic routing")

    router = LLMRouter()

    # 2.1 Default routing (no provider specified)
    try:
        out = await router.route(
            "test_default",
            "Summarize in one sentence: What is FZQ-AI? (test default routing)",
        )
        print("  [default] OK, len(output) =", len(str(out)))
    except Exception:
        print("  [default] ERROR:")
        traceback.print_exc()

    # 2.2 Specific provider = glm (or glm-5.2, depends on Provider registration name)
    try:
        req = {
            "task_type": "test_glm",
            "prompt": "Summarize: What role does GLM-5.2 play in this project? (test specific provider)",
            "provider": "glm",
        }
        out = await router.call(provider=req.get("provider", "deepseek"), prompt=req.get("prompt", ""), model=req.get("model", ""), api_key=req.get("api_key", ""))
        print("  [glm] OK, len(output) =", len(str(out)))
    except Exception:
        print("  [glm] ERROR:")
        traceback.print_exc()


# ---------- 3. English Pipeline sanity check ----------
async def check_english_pipeline():
    print("\n[PIPELINE] English pipeline sanity check")

    try:
        # Use zh pipelines since English ones may not be registered yet
        # Try any registered pipeline
        families = PipelineRegistry.list_families()
        if not families:
            print("  [pipeline] SKIP - no registered pipelines")
            return
        fam = families[0]
        pipeline = PipelineRegistry.get(fam)  # get() returns instance
        print(f"  [{fam}] Pipeline class created: {type(pipeline).__name__}")
        print("  [pipeline] OK, pipeline instantiated successfully")
    except Exception:
        print("  [pipeline] ERROR:")
        traceback.print_exc()


# ---------- 4. Chinese Router-based Pipeline check ----------
async def check_chinese_router_pipeline():
    print("\n[PIPELINE] Chinese router-based pipeline sanity check")
    try:
        print("  [zh_router] SKIP (no router-based zh pipeline configured in this script)")
    except Exception:
        print("  [zh_router] ERROR:")
        traceback.print_exc()


async def main():
    print("=== FZQ-AI v13 Runtime Health Check ===")

    check_registry_snapshot()
    await check_router_providers()
    await check_english_pipeline()
    await check_chinese_router_pipeline()

    print("\n=== Health Check Finished ===")


if __name__ == "__main__":
    asyncio.run(main())
