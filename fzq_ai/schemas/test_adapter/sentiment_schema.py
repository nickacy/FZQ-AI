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

    id: str = Field(default="mock-sentiment-123", description="Unique identifier")
    label: SentimentLabel = Field(default=SentimentLabel.NEUTRAL, description="Sentiment label")
    score: float = Field(default=0.0, ge=-1, le=1, description="Sentiment score")
    subject: Optional[str] = Field(default="mock-subject", description="Subject of analysis")
    context: Optional[str] = Field(default="mock-context", description="Context")
    confidence: Optional[float] = Field(default=1.0, ge=0, le=1, description="Confidence score")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Analysis timestamp")
    source_ids: List[str] = Field(default_factory=list, description="Source references")
