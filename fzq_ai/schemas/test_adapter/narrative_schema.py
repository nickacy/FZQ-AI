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

    id: str = Field(default="mock-narrative-123", description="Unique identifier")
    dimension: AnalysisDimension = Field(default=AnalysisDimension.ECONOMIC, description="Analysis dimension")
    summary: str = Field(default="Mock narrative summary.", description="Narrative summary")
    key_entities: List[str] = Field(default_factory=list, description="Key entities")
    themes: List[str] = Field(default_factory=list, description="Identified themes")
    confidence: Optional[float] = Field(default=1.0, ge=0, le=1, description="Confidence score")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
