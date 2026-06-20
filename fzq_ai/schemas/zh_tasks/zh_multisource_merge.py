from pydantic import BaseModel, Field
from typing import List, Optional


class ZhMultiSourceMainAxis(BaseModel):
    what: Optional[str] = None
    when: Optional[str] = None
    where: Optional[str] = None
    who: Optional[str] = None
    why: Optional[str] = None
    how: Optional[str] = None


class ZhMultiSourcePerspectiveDiff(BaseModel):
    dimension: Optional[str] = Field(None, description="归因 / 措辞强度 / 被引主体 / 时间线侧重 / 数据口径")
    source_a: Optional[str] = None
    source_b: Optional[str] = None
    diff: Optional[str] = None


class ZhMultiSourceReliability(BaseModel):
    source: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None


class ZhMultiSourceMergeOutput(BaseModel):
    task_type: str = "zh_multisource_merge"
    event_id: Optional[str] = None
    main_axis: Optional[ZhMultiSourceMainAxis] = None
    perspective_diffs: List[ZhMultiSourcePerspectiveDiff] = []
    source_reliability: List[ZhMultiSourceReliability] = []
    consistency_score: Optional[float] = None
