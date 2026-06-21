# fzq_ai/schemas/pipeline_output.py
# Phase 4‑5 最终版：完整结构化情报输出 Schema

from typing import List
from pydantic import Field
from .base import PipelineOutputSchema


# ------------------------------------------------------------
# News Pipeline Output
# ------------------------------------------------------------
class NewsPipelineOutput(PipelineOutputSchema):
    raw_input_count: int
    summaries: List[str]
    task_status: str = "completed"


# ------------------------------------------------------------
# Narrative Pipeline Output
# ------------------------------------------------------------
class NarrativePipelineOutput(PipelineOutputSchema):
    narrative_text: str
    task_status: str = "completed"


# ------------------------------------------------------------
# Risk Pipeline Output
# ------------------------------------------------------------
class RiskPipelineOutput(PipelineOutputSchema):
    summary: str
    factors: str
    forecast: str
    task_status: str = "completed"


# ------------------------------------------------------------
# Sentiment Pipeline Output
# ------------------------------------------------------------
class SentimentPipelineOutput(PipelineOutputSchema):
    score: float
    summary: str
    task_status: str = "completed"


# ------------------------------------------------------------
# Scenario Pipeline Output
# ------------------------------------------------------------
class ScenarioPipelineOutput(PipelineOutputSchema):
    scenarios: str
    task_status: str = "completed"


# ------------------------------------------------------------
# Daily Report Pipeline Output（最终结构化情报对象）
# ------------------------------------------------------------
class DailyReportPipelineOutput(PipelineOutputSchema):
    """
    Phase 4‑5：最终结构化日报 Schema
    包含：
    - 最终日报文本（LLM 生成）
    - 所有子模块的结构化结果
    """

    # 最终日报文本（LLM 生成）
    report_content: str

    # 子模块结构化结果
    news: NewsPipelineOutput
    narrative: NarrativePipelineOutput
    risk: RiskPipelineOutput
    sentiment: SentimentPipelineOutput
    scenario: ScenarioPipelineOutput

    # 统计字段
    news_count: int

    task_status: str = "completed"
