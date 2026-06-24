import pytest
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline


@pytest.mark.asyncio
async def test_merge_pipeline():
    pipeline = ZhMultiSourceMergePipeline()
    result = await pipeline.run_async(
        event_topic="test event",
        sources=[
            {"title": "A", "content": "AAA"},
            {"title": "B", "content": "BBB"},
        ],
    )
    # Pipeline returns ZhMultiSourceMergeOutput Pydantic model
    assert result is not None
    assert result.task_type == "zh_multisource_merge"
