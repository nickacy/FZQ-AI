import asyncio
from fzq_ai.pipelines import get_pipeline

async def main():
    pipeline = get_pipeline("zh_multisource_merge@v1")
    result = await pipeline.run(
        event_topic="测试事件",
        sources=[
            {"title": "A", "content": "AAA"},
            {"title": "B", "content": "BBB"},
        ],
    )
    # 打印完整结果（包括 raw 和 cleaned）
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))

asyncio.run(main())
