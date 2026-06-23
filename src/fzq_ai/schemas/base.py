# fzq_ai/schemas/base.py

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class PipelineOutputSchema(BaseModel):
    """所有 Pipeline 输出的基础 Schema"""

    generate_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC 时间，表示该结果生成时间",
    )
    task_status: str = Field(
        default="completed",
        description="任务状态，如 completed / failed / partial 等",
    )
