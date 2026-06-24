from fzq_ai.pipelines.zh_multisource_merge import ZhMultiSourceMergePipeline

def test_merge_pipeline():
    pipeline = ZhMultiSourceMergePipeline()
    result = pipeline.run({"input": "中国经济最新动态"})
    assert "summary" in result
    assert "clusters" in result
