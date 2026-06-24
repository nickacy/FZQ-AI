import fzq_ai.pipelines
import asyncio
from fzq_ai.pipelines.registry import PipelineRegistry


async def check_pipeline(name: str, **kwargs):
    print(f"\n[CHECK] {name} + GLM-5.2")

    pipeline = PipelineRegistry.get(name)  # get() returns instance via create()

    try:
        if hasattr(pipeline, 'run_async'):
            result = await pipeline.run_async(**kwargs)
        else:
            result = await pipeline.run(**kwargs)
        print("  -> OK, type:", type(result))
        status = result.get("status") if isinstance(result, dict) else getattr(result, "status", getattr(result, "task_type", "N/A"))
        print("  -> status:", status)
    except Exception as e:
        print("  -> ERROR:")
        raise


async def main():
    sources = [
        {"title": "A", "content": "AAA"},
        {"title": "B", "content": "BBB"},
    ]

    await check_pipeline(
        "zh_multisource_merge@v1",
        event_topic="测试事件",
        sources=sources,
    )

    await check_pipeline(
        "zh_opinion_landscape@v1",
        topic="测试主题",
        sources=sources,
    )

    await check_pipeline(
        "zh_policy_brief@v1",
        topic="测试政策",
        sources=sources,
    )

    await check_pipeline(
        "zh_risk_scan@v1",
        topic="测试风险",
        sources=sources,
    )


if __name__ == "__main__":
    asyncio.run(main())
