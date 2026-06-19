from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ScenarioProjection(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-projection-123", description="Unique identifier")
    name: str = Field(default="Mock Scenario", description="Scenario name")
    time_horizon: str = Field(default="1M", description="Time horizon")
    assumptions: List[str] = Field(default_factory=list, description="Key assumptions")
    projected_values: Dict[str, Any] = Field(default_factory=dict, description="Projected values")
    probability: Optional[float] = Field(default=1.0, ge=0, le=1, description="Probability")


class ScenarioAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-scenario-analysis-123", description="Unique identifier")
    projections: List[ScenarioProjection] = Field(default_factory=list, description="Scenario projections")
    baseline: Optional[str] = Field(default="mock-baseline", description="Baseline scenario ID")
    selected_scenario: Optional[str] = Field(default="mock-selected", description="Selected scenario ID")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
