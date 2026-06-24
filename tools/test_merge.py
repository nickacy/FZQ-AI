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
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
