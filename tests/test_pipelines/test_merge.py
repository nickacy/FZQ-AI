# tests/test_pipelines/test_merge.py

from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline
from tests.utils.mock_provider import MockProvider

def test_merge_pipeline():
    pipeline = ZhMultiSourceMergePipeline(provider=MockProvider())
    result = pipeline.run({"input": "中国经济最新动态"})

    assert isinstance(result, dict)
    assert "summary" in result
    assert "clusters" in result
