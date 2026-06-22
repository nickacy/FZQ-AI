# fzq_ai/pipelines/scenario_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult


BASE_CASE_TEMPLATE = PromptTemplate("""
You are a scenario analysis expert. Provide the most likely base case scenario
for the next 30–90 days, including:
- Key drivers
- Expected trajectory
- Strategic implications

Topic: $query
""")

ALTERNATIVE_SCENARIOS_TEMPLATE = PromptTemplate("""
List 2–3 plausible alternative scenarios (e.g., upside / downside) for the next 30–90 days.
For each scenario, include:
- Scenario name
- Short description
- Probability (low/medium/high)

Topic: $query
""")

KEY_DRIVERS_TEMPLATE = PromptTemplate("""
Identify 5 key drivers or triggers that could shift the scenario trajectory.

Topic: $query
""")

IMPLICATIONS_TEMPLATE = PromptTemplate("""
Summarize the main implications of the base case scenario for the next 30–90 days.

Topic: $query
""")


class ScenarioPipeline(BasePipeline):
    """Scenario analysis with concurrent sub-tasks."""

    def __init__(self):
        self.llm = LLMRouter()

    async def run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        tasks = [
            self.llm.route("scenario_base_case", BASE_CASE_TEMPLATE.render(query=query)),
            self.llm.route("scenario_alternatives", ALTERNATIVE_SCENARIOS_TEMPLATE.render(query=query)),
            self.llm.route("scenario_drivers", KEY_DRIVERS_TEMPLATE.render(query=query)),
            self.llm.route("scenario_implications", IMPLICATIONS_TEMPLATE.render(query=query)),
        ]

        base_case, alternatives, drivers, implications = await asyncio.gather(*tasks)

        return ServiceResult.ok({
            "base_case": base_case,
            "alternatives": alternatives,
            "drivers": drivers,
            "implications": implications,
        })
