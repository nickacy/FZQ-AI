# Pydantic schemas for the 4 zh_tasks pipelines.
from fzq_ai.schemas.zh_tasks.zh_policy_brief import (
    ZhPolicyBriefOutput,
    ZhPolicyBriefKeyPoint,
    ZhPolicyBriefAffectedEntity,
    ZhPolicyBriefTimelineItem,
    ZhPolicyBriefQuantitativeTarget,
)
from fzq_ai.schemas.zh_tasks.zh_risk_scan import (
    ZhRiskScanOutput,
    ZhRiskScanRiskItem,
    ZhRiskEvidenceItem,
)
from fzq_ai.schemas.zh_tasks.zh_opinion_landscape import (
    ZhOpinionLandscapeOutput,
    ZhOpinionCluster,
    ZhOpinionFrame,
    ZhOpinionInfluencer,
    ZhOpinionHeatPoint,
    ZhOpinionQuote,
)
from fzq_ai.schemas.zh_tasks.zh_multisource_merge import (
    ZhMultiSourceMergeOutput,
)


__all__ = [
    # policy_brief
    "ZhPolicyBriefOutput",
    "ZhPolicyBriefKeyPoint",
    "ZhPolicyBriefAffectedEntity",
    "ZhPolicyBriefTimelineItem",
    "ZhPolicyBriefQuantitativeTarget",
    # risk_scan
    "ZhRiskScanOutput",
    "ZhRiskScanRiskItem",
    "ZhRiskEvidenceItem",
    # opinion_landscape
    "ZhOpinionLandscapeOutput",
    "ZhOpinionCluster",
    "ZhOpinionFrame",
    "ZhOpinionInfluencer",
    "ZhOpinionHeatPoint",
    "ZhOpinionQuote",
    # multisource_merge
    "ZhMultiSourceMergeOutput",
]


# Schema registry by task_type — used by ZhStructuredPipeline to pick the
# Pydantic output class without each subclass re-declaring an import.
SCHEMA_BY_TASK: dict[str, type] = {
    "zh_policy_brief": ZhPolicyBriefOutput,
    "zh_risk_scan": ZhRiskScanOutput,
    "zh_opinion_landscape": ZhOpinionLandscapeOutput,
    "zh_multisource_merge": ZhMultiSourceMergeOutput,
}
