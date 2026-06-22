from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


# -----------------------------------------
# 5W1H 单项（三态：一致 / 分歧 / 缺失）
# -----------------------------------------
class ZhMultiSourceAxisItem(BaseModel):
    value: Optional[str] = Field(
        None,
        description="该要素的综合描述（在一致或分歧时给出）"
    )
    status: Literal["一致", "分歧", "缺失"] = Field(
        ...,
        description="该要素在多源中的状态：一致 / 分歧 / 缺失"
    )


# -----------------------------------------
# 5W1H 主轴（what / when / where / who / why / how）
# -----------------------------------------
class ZhMultiSourceMainAxis(BaseModel):
    what: ZhMultiSourceAxisItem
    when: ZhMultiSourceAxisItem
    where: ZhMultiSourceAxisItem
    who: ZhMultiSourceAxisItem
    why: ZhMultiSourceAxisItem
    how: ZhMultiSourceAxisItem


# -----------------------------------------
# 多源视角差异（5 个维度）
# -----------------------------------------
class ZhMultiSourcePerspectiveDiff(BaseModel):
    dimension: Literal[
        "归因",
        "措辞强度",
        "被引主体",
        "时间线侧重",
        "数据口径",
        "其他"
    ] = Field(..., description="差异维度")

    source_a: str = Field(..., description="信源 A 标识")
    source_b: str = Field(..., description="信源 B 标识")

    diff: str = Field(..., description="差异的具体描述")
    evidence_span: str = Field(
        ...,
        max_length=80,
        description="支撑该差异的原文片段"
    )

    @field_validator("source_a", "source_b", "diff", "evidence_span")
    def must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("多源差异字段不能为空")
        return v


# -----------------------------------------
# 信源可靠性评分
# -----------------------------------------
class ZhMultiSourceReliability(BaseModel):
    source: str = Field(..., description="信源名称或标识")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.0–1.0 的可靠性评分"
    )
    reason: str = Field(..., description="评分理由")
    bias_hint: Optional[str] = Field(
        None,
        description="可能的偏向性提示（如立场、利益相关）"
    )

    @field_validator("source", "reason")
    def must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("信源可靠性字段不能为空")
        return v


# -----------------------------------------
# 证据映射（全局 evidence_map）
# -----------------------------------------
class ZhMultiSourceEvidenceItem(BaseModel):
    item_id: str = Field(..., description="原始条目的唯一标识")
    span: str = Field(..., max_length=80, description="原文片段")
    source: str = Field(..., description="信源名称或标识")

    @field_validator("item_id", "span", "source")
    def evidence_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("证据映射字段不能为空")
        return v


# -----------------------------------------
# 顶层输出结构
# -----------------------------------------
class ZhMultiSourceMergeOutput(BaseModel):
    task_type: Literal["zh_multisource_merge"] = "zh_multisource_merge"

    event_id: Optional[str] = Field(
        None,
        description="事件唯一标识（可由上游生成）"
    )

    # 5W1H 主轴（带三态）
    main_axis: Optional[ZhMultiSourceMainAxis] = None

    # 多源视角差异矩阵
    perspective_diffs: List[ZhMultiSourcePerspectiveDiff] = Field(
        default_factory=list
    )

    # 信源可靠性评分
    source_reliability: List[ZhMultiSourceReliability] = Field(
        default_factory=list
    )

    # 一致性评分（0–1）
    consistency_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="多源报道之间的一致性评分"
    )

    # 缺失视角（如缺少某地区、某立场、某关键主体）
    missing_sources: List[str] = Field(
        default_factory=list,
        description="在该事件中明显缺位的视角或信源"
    )

    # 冲突视角（明显互相矛盾的报道或叙事）
    conflict_sources: List[str] = Field(
        default_factory=list,
        description="在该事件中存在明显冲突的视角或信源"
    )

    # 全局证据映射
    evidence_map: List[ZhMultiSourceEvidenceItem] = Field(
        default_factory=list,
        description="用于溯源的全局证据列表"
    )
