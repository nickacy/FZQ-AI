from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AnalysisDimension(str, Enum):
    ECONOMIC = "economic"
    POLITICAL = "political"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    LEGAL = "legal"
    ENVIRONMENTAL = "environmental"
    GEOPOLITICAL = "geopolitical"
    MARKET = "market"


class NarrativeAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    dimension: AnalysisDimension = Field(..., description="Analysis dimension")
    summary: str = Field(..., description="Narrative summary")
    key_entities: List[str] = Field(default_factory=list, description="Key entities")
    themes: List[str] = Field(default_factory=list, description="Identified themes")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score")
    timestamp: Optional[datetime] = Field(default=None, description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
