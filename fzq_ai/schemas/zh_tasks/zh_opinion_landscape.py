from pydantic import BaseModel, Field
from typing import List, Optional


class ZhOpinionCamp(BaseModel):
    camp_id: str
    label: str
    stance: str = Field(..., description="支持 / 反对 / 中立 / 复杂")
    share: float = Field(..., ge=0, le=1)
    core_claim: Optional[str] = None
    representative_quotes: List[str] = []


class ZhOpinionFrame(BaseModel):
    frame: Optional[str] = None
    used_by: List[str] = []
    effect: Optional[str] = None


class ZhOpinionKeyNode(BaseModel):
    author: Optional[str] = None
    platform: Optional[str] = None
    camp: Optional[str] = None
    influence_score: Optional[float] = None


class ZhOpinionHeat(BaseModel):
    volume: Optional[int] = None
    trend: Optional[str] = Field(None, description="上升 / 下降 / 平稳 / 震荡")
    peak_date: Optional[str] = None


class ZhOpinionLandscapeOutput(BaseModel):
    task_type: str = "zh_opinion_landscape"
    topic: Optional[str] = None
    camps: List[ZhOpinionCamp] = []
    frame_analysis: List[ZhOpinionFrame] = []
    key_nodes: List[ZhOpinionKeyNode] = []
    heat: Optional[ZhOpinionHeat] = None
