# fzq_ai/pipelines/risk_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base_pipeline import BasePipeline
from fzq_ai.domain.models import ServiceResult


RISK_SUMMARY_TEMPLATE = PromptTemplate("Generate a risk summary:\nTopic: $query")
RISK_FACTORS_TEMPLATE = PromptTemplate("List 5 key risk factors:\nTopic: $query")
RISK_FORECAST_TEMPLATE = PromptTemplate("Predict risk trend for next 30 days:\nTopic: $query")


class RiskPipeline(BasePipeline):

    def __init__(self):
        self.llm = LLMRouter()

    async def run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        return await self._measure("risk_pipeline", self._run_impl(query))

    async def _run_impl(self, query: str) -> ServiceResult:
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
