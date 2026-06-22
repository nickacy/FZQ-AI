from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


# -----------------------------------------
# 证据链结构（严格要求非空）
# -----------------------------------------
class ZhRiskEvidenceItem(BaseModel):
    item_id: str = Field(..., description="来源 item 的唯一标识")
    span: str = Field(..., max_length=60, description="原文片段，必须为直接引用")
    source: str = Field(..., description="来源渠道，如 news / social / report")

    @field_validator("item_id", "span", "source")
    def must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("证据链字段不能为空")
        return v


# -----------------------------------------
# 风险项结构（严格枚举 + 强制字段）
# -----------------------------------------
class ZhRiskScanRiskItem(BaseModel):
    risk_id: str = Field(..., description="风险项唯一标识")

    # Prompt 明确要求的 7 类风险分类
    category: Literal[
        "地缘", "金融", "舆情", "合规", "供应链", "技术", "其他"
    ]

    # Prompt 明确要求的 4 档风险等级
    level: Literal["高", "中", "低", "观察"]

    title: str = Field(..., description="风险标题")
    summary: str = Field(..., description="风险摘要，基于原文证据")

    evidence: List[ZhRiskEvidenceItem] = Field(
        default_factory=list,
        description="证据链（必须唯一且基于原文）"
    )

    convey_chain: List[str] = Field(
        default_factory=list,
        description="风险传导链，如 A → B → C"
    )

    affected_entities: List[str] = Field(
        default_factory=list,
        description="受影响主体列表"
    )

    suggested_action: str = Field(
        ...,
        description="可执行行动建议（模板化）"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.0–1.0 浮点数，符合 Prompt 的置信度分级标准"
    )


# -----------------------------------------
# 顶层结构（新增字段：overall_risk_level / entity_watchlist / suggested_actions）
# -----------------------------------------
class ZhRiskScanOutput(BaseModel):
    task_type: Literal["zh_risk_scan"] = "zh_risk_scan"

    scan_window: Optional[str] = Field(
        None,
        description="扫描窗口，如 '24h' / '7d'"
    )

    # 风险项列表
    risks: List[ZhRiskScanRiskItem] = Field(default_factory=list)

    # Prompt 要求的整体风险等级（4 档）
    overall_risk_level: Optional[Literal["高", "中", "低", "观察"]] = None

    # 主体监控列表（Prompt 强制要求）
    entity_watchlist: List[str] = Field(default_factory=list)

    # 全局行动建议（Prompt 强制要求）
    suggested_actions: List[str] = Field(default_factory=list)

    # 风险扫描总结
    summary: Optional[str] = None

    # 全局置信度（Prompt 强制要求）
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="整体分析置信度"
    )
