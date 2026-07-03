"""V24 — zh_policy_brief pipeline (refactored to use ZhStructuredPipeline)."""
from fzq_ai.pipelines._zh_pipeline import ZhStructuredPipeline


class ZhPolicyBriefPipeline(ZhStructuredPipeline):
    task_type = "zh_policy_brief"
    prompt_path = "zh/zh_policy_brief.txt"


# Registry alias
ZhPolicyBrief = ZhPolicyBriefPipeline
