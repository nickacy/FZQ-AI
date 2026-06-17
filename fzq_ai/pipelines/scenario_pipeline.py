# fzq_ai/pipelines/scenario_pipeline.py

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult


SCENARIO_TEMPLATE = PromptTemplate("""
You are a geopolitical scenario analysis expert. Generate 3 possible scenarios for the next 30 days:

Topic: $query

Output:
1. Scenario name
2. Trigger factors
3. Possible development path
4. Risk level (low/medium/high)
""")


class ScenarioPipeline(BasePipeline):
    """Scenario planning pipeline."""

    def __init__(self):
        self.llm = LLMRouter()

    async def _run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        prompt = SCENARIO_TEMPLATE.render(query=query)
        result = await self.llm.route("scenario", prompt)
        return ServiceResult.ok(result)
