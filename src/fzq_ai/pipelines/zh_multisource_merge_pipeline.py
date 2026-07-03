"""V24 — zh_multisource_merge pipeline (refactored to use ZhStructuredPipeline)."""
from fzq_ai.pipelines._zh_pipeline import ZhStructuredPipeline


class ZhMultisourceMergePipeline(ZhStructuredPipeline):
    task_type = "zh_multisource_merge"
    prompt_path = "zh/zh_multisource_merge.txt"


# Registry aliases
ZhMultiSourceMerge = ZhMultisourceMergePipeline
ZhMultiSourceMergePipeline = ZhMultisourceMergePipeline
