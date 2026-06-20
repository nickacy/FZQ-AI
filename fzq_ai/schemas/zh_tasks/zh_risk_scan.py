from pydantic import BaseModel, Field
from typing import List, Optional


class ZhRiskEvidenceItem(BaseModel):
    item_id: Optional[str] = None
    span: Optional[str] = None
    source: Optional[str] = None


class ZhRiskScanRiskItem(BaseModel):
    risk_id: Optional[str] = None
    category: str = Field(..., description="地缘 / 金融 / 舆情 / 合规 / 供应链 / 技术")
    level: str = Field(..., description="高 / 中 / 低 / 观察")
    title: Optional[str] = None
    summary: Optional[str] = None
    evidence: List[ZhRiskEvidenceItem] = []
    convey_chain: List[str] = Field(default_factory=list, description="A → B → C")
    affected_entities: List[str] = []
    suggested_action: Optional[str] = None
    confidence: Optional[float] = None


class ZhRiskScanOutput(BaseModel):
    task_type: str = "zh_risk_scan"
    scan_window: Optional[str] = None
    risks: List[ZhRiskScanRiskItem] = []
    summary: Optional[str] = None
