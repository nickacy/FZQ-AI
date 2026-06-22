from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


# ---------------------------------------------------------
# 代表性引用（必须带 item_id）
# ---------------------------------------------------------
class ZhOpinionQuote(BaseModel):
    item_id: str = Field(..., description="引用来源的唯一标识")
    span: str = Field(..., max_length=80, description="原文片段，必须为直接引用")

    @field_validator("item_id", "span")
    def must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("引用字段不能为空")
        return v


# ---------------------------------------------------------
# 舆论阵营（clusters）
# ---------------------------------------------------------
class ZhOpinionCluster(BaseModel):
    cluster_id: str = Field(..., description="阵营编号")
    label: str = Field(..., description="阵营标签")

    stance: Literal["支持", "反对", "中性", "复杂"] = Field(
        ..., description="阵营立场"
    )
    sentiment: Literal["正面", "负面", "中性", "混合"] = Field(
        ..., description="情绪倾向"
    )

    size: int = Field(..., ge=1, description="阵营规模（人数或样本量）")

    key_arguments: List[str] = Field(
        default_factory=list,
        description="阵营的关键论点"
    )

    representative_quotes: List[ZhOpinionQuote] = Field(
        default_factory=list,
        description="阵营代表性引用"
    )


# ---------------------------------------------------------
# 叙事框架（10 个标准框架）
# ---------------------------------------------------------
class ZhOpinionFrame(BaseModel):
    frame: str = Field(..., description="框架名称，如 '责任归因'")
    description: str = Field(..., description="框架描述")
    evidence_span: str = Field(..., max_length=80, description="原文片段")

    @field_validator("frame", "description", "evidence_span")
    def must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("框架字段不能为空")
        return v


# ---------------------------------------------------------
# 意见领袖（influencers）
# ---------------------------------------------------------
class ZhOpinionInfluencer(BaseModel):
    name: str = Field(..., description="主体名称")
    influence_score: float = Field(..., ge=0.0, le=1.0)
    stance: Literal["支持", "反对", "中性", "复杂"]
    representative_quotes: List[ZhOpinionQuote] = Field(default_factory=list)


# ---------------------------------------------------------
# 热度趋势（heat_trend）
# ---------------------------------------------------------
class ZhOpinionHeatPoint(BaseModel):
    date: str = Field(..., description="日期 YYYY-MM-DD")
    volume: int = Field(..., ge=0, description="当天热度值")


# ---------------------------------------------------------
# 顶层结构（舆论版图分析输出）
# ---------------------------------------------------------
class ZhOpinionLandscapeOutput(BaseModel):
    task_type: Literal["zh_opinion_landscape"] = "zh_opinion_landscape"

    topic: Optional[str] = None
    time_range: Optional[str] = None

    # 舆论阵营（聚类结果）
    clusters: List[ZhOpinionCluster] = Field(default_factory=list)

    # 立场分布（支持/反对/中性/复杂）
    stance_map: List[str] = Field(default_factory=list)

    # 情绪分布（正面/负面/中性/混合）
    sentiment_map: List[str] = Field(default_factory=list)

    # 叙事框架（10 个标准框架）
    key_frames: List[ZhOpinionFrame] = Field(default_factory=list)

    # 关键意见领袖
    influencers: List[ZhOpinionInfluencer] = Field(default_factory=list)

    # 热度趋势（时间序列）
    heat_trend: List[ZhOpinionHeatPoint] = Field(default_factory=list)

    # 全局代表性引用
    representative_quotes: List[ZhOpinionQuote] = Field(default_factory=list)

    # 全局立场
    overall_stance: Optional[Literal["支持", "反对", "中性", "复杂"]] = None

    # 全局情绪
    overall_sentiment: Optional[Literal["正面", "负面", "中性", "混合"]] = None

    # 全局置信度
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="整体分析置信度"
    )
