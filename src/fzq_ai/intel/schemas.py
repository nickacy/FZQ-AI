# fzq_ai/intel/schemas.py

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class EventSchema(BaseModel):
    title: str
    date: Optional[str] = None
    region: Optional[str] = None
    summary: str


class IntelSchema(BaseModel):
    language: str
    regions: List[str]
    events: List[EventSchema]
    stats: Dict[str, Any]
