from pydantic import BaseModel, Field
from typing import List, Optional


class ZhPolicyBriefKeyPoint(BaseModel):
    point: str
    category: str = Field(..., description="目标 / 执行 / 适用对象 / 配套措施 / 约束 / 其他")
    evidence_span: Optional[str] = None


class ZhPolicyBriefAffectedEntity(BaseModel):
    entity: str
    role: str = Field(..., description="执行方 / 适用方 / 监管方 / 受益方 / 约束方")
    impact: str = Field(..., description="正面 / 负面 / 中性 / 混合")


class ZhPolicyBriefTimelineItem(BaseModel):
    date: Optional[str] = None
    event: Optional[str] = None
    type: Optional[str] = Field(None, description="发布 / 生效 / 试点 / 评估 / 废止")


class ZhPolicyBriefQuantitativeTarget(BaseModel):
    metric: Optional[str] = None
    value: Optional[str] = None
    deadline: Optional[str] = None


class ZhPolicyBriefOutput(BaseModel):
    task_type: str = "zh_policy_brief"
    doc_id: Optional[str] = None
    summary: Optional[str] = None
    key_points: List[ZhPolicyBriefKeyPoint] = []
    affected_entities: List[ZhPolicyBriefAffectedEntity] = []
    timeline: List[ZhPolicyBriefTimelineItem] = []
    quantitative_targets: List[ZhPolicyBriefQuantitativeTarget] = []
    risk_flags: List[str] = []
    confidence: Optional[float] = None
