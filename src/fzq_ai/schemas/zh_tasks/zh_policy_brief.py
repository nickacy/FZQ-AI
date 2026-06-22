from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


# -------------------------
# 子结构：Key Points
# -------------------------
class ZhPolicyBriefKeyPoint(BaseModel):
    point: str = Field(..., max_length=60)
    category: Literal["目标", "执行", "适用对象", "配套措施", "约束", "其他"]
    evidence_span: str = Field(..., max_length=30)

    @field_validator("evidence_span")
    def evidence_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("evidence_span 不能为空，必须为原文片段")
        return v


# -------------------------
# 子结构：Affected Entities
# -------------------------
class ZhPolicyBriefAffectedEntity(BaseModel):
    entity: str
    role: Literal["执行方", "适用方", "监管方", "受益方", "约束方"]
    impact: Literal["正面", "负面", "中性", "混合"]


# -------------------------
# 子结构：Timeline
# -------------------------
class ZhPolicyBriefTimelineItem(BaseModel):
    date: Optional[str] = None
    event: Optional[str] = None
    type: Optional[Literal["发布", "生效", "试点", "评估", "废止"]] = None


# -------------------------
# 子结构：Quantitative Targets
# -------------------------
class ZhPolicyBriefQuantitativeTarget(BaseModel):
    metric: str
    value: str
    deadline: str


# -------------------------
# 顶层结构：Policy Brief Output
# -------------------------
class ZhPolicyBriefOutput(BaseModel):
    task_type: Literal["zh_policy_brief"] = "zh_policy_brief"
    doc_id: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=200)

    key_points: List[ZhPolicyBriefKeyPoint] = Field(default_factory=list)
    affected_entities: List[ZhPolicyBriefAffectedEntity] = Field(default_factory=list)
    timeline: List[ZhPolicyBriefTimelineItem] = Field(default_factory=list)
    quantitative_targets: List[ZhPolicyBriefQuantitativeTarget] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)

    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="0.0–1.0 浮点数，符合 Prompt 的置信度分级标准"
    )
