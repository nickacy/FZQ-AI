from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class SentimentAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    label: SentimentLabel = Field(..., description="Sentiment label")
    score: float = Field(..., ge=-1, le=1, description="Sentiment score")
    subject: Optional[str] = Field(default=None, description="Subject of analysis")
    context: Optional[str] = Field(default=None, description="Context")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence score")
    timestamp: Optional[datetime] = Field(default=None, description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
