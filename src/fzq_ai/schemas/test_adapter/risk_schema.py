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

    id: str = Field(default="mock-risk-factor-123", description="Unique identifier")
    name: str = Field(default="Mock Risk Factor", description="Risk factor name")
    category: str = Field(default="mock-category", description="Risk category")
    level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk level")
    probability: Optional[float] = Field(default=1.0, ge=0, le=1, description="Probability")
    impact: Optional[float] = Field(default=1.0, ge=0, le=1, description="Impact score")
    description: Optional[str] = Field(default="Mock risk description.", description="Detailed description")
    mitigation: Optional[str] = Field(default="Mock mitigation strategy.", description="Mitigation strategy")


class RiskAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-risk-analysis-123", description="Unique identifier")
    factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors")
    overall_level: RiskLevel = Field(default=RiskLevel.LOW, description="Overall risk level")
    summary: str = Field(default="Mock risk summary.", description="Risk summary")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
