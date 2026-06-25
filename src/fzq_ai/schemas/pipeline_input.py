from pydantic import BaseModel
from typing import Optional

class PipelineInput(BaseModel):
    query: str
    target_language: str = "zh"
    task_type: str = "daily_report"
    region: Optional[str] = None
