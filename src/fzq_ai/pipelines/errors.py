from pydantic import BaseModel
from typing import Optional


class PipelineError(BaseModel):
    message: str
    stage: str
    provider: Optional[str] = None
