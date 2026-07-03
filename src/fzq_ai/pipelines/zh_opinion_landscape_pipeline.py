"""V24 — zh_opinion_landscape pipeline (refactored to use ZhStructuredPipeline)."""
from fzq_ai.pipelines._zh_pipeline import ZhStructuredPipeline


class ZhOpinionLandscapePipeline(ZhStructuredPipeline):
    task_type = "zh_opinion_landscape"
    prompt_path = "zh/zh_opinion_landscape.txt"


# Registry alias
ZhOpinionLandscape = ZhOpinionLandscapePipeline
