import pytest
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline


@pytest.mark.asyncio
async def test_merge_pipeline():
    pipeline = ZhMultiSourceMergePipeline()
    result = await pipeline.run(req={"input": "test merge topic"})
    # Pipeline returns ZhMultiSourceMergeOutput Pydantic model
    assert result is not None
    assert result.get("task_type") == "zh_multisource_merge" or result.get("task") == "zh_multisource_merge"
