# fzq_ai/pipelines/risk_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult


RISK_SUMMARY_TEMPLATE = PromptTemplate("""
You are a risk analysis expert. Generate a risk summary for the following topic:

Topic: $query
""")

RISK_FACTORS_TEMPLATE = PromptTemplate("""
List 5 key risk factors for the following topic:

Topic: $query
""")

RISK_FORECAST_TEMPLATE = PromptTemplate("""
Predict the risk trend (up/down/stable) for the next 30 days and explain why:

Topic: $query
""")


class RiskPipeline(BasePipeline):
    """Risk analysis with concurrent sub-tasks."""

    def __init__(self):
        self.llm = LLMRouter()

    async def run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        tasks = [
            self.llm.route("risk_summary", RISK_SUMMARY_TEMPLATE.render(query=query)),
            self.llm.route("risk_factors", RISK_FACTORS_TEMPLATE.render(query=query)),
            self.llm.route("risk_forecast", RISK_FORECAST_TEMPLATE.render(query=query)),
        ]
        summary, factors, forecast = await asyncio.gather(*tasks)
        return ServiceResult.ok({
            "summary": summary,
            "factors": factors,
            "forecast": forecast,
        })
