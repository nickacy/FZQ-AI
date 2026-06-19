from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFactor(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Risk factor name")
    category: str = Field(..., description="Risk category")
    level: RiskLevel = Field(..., description="Risk level")
    probability: Optional[float] = Field(default=None, ge=0, le=1, description="Probability")
    impact: Optional[float] = Field(default=None, ge=0, le=1, description="Impact score")
    description: Optional[str] = Field(default=None, description="Detailed description")
    mitigation: Optional[str] = Field(default=None, description="Mitigation strategy")


class RiskAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors")
    overall_level: RiskLevel = Field(..., description="Overall risk level")
    summary: str = Field(..., description="Risk summary")
    timestamp: Optional[datetime] = Field(default=None, description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
