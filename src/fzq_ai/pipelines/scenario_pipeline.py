import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate
from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.domain.models import ServiceResult


BASE_SCENARIO_TEMPLATE = PromptTemplate("""
You are a scenario analysis expert. Define the most likely base case scenario
for the following topic over the next 30–90 days, including key drivers and
expected trajectory.

Topic: $query
""")

ALTERNATIVE_SCENARIOS_TEMPLATE = PromptTemplate("""
List 2–3 plausible alternative scenarios (e.g., upside / downside) for the
following topic over the next 30–90 days. For each scenario, give:
- A short name
- A brief description
- Rough probability (low/medium/high)

Topic: $query
""")

KEY_DRIVERS_TEMPLATE = PromptTemplate("""
Identify 5 key drivers or triggers that would shift the scenario trajectory
for the following topic (policy moves, market shocks, geopolitical events, etc.).

Topic: $query
""")

SCENARIO_IMPLICATIONS_TEMPLATE = PromptTemplate("""
Summarize the main implications of the base case scenario for the next 30–90 days
(e.g., risk, opportunity, operational impact).

Topic: $query
""")


class ScenarioPipeline(BasePipeline):
    """Scenario analysis with concurrent sub-tasks."""

    def __init__(self):
        self.llm = LLMRouter()

    async def _run_async(self, *args, query: str = "", **kwargs) -> ServiceResult:
        tasks = [
            self.llm.route("scenario_base", BASE_SCENARIO_TEMPLATE.render(query=query)),
            self.llm.route("scenario_alternatives", ALTERNATIVE_SCENARIOS_TEMPLATE.render(query=query)),
            self.llm.route("scenario_drivers", KEY_DRIVERS_TEMPLATE.render(query=query)),
            self.llm.route("scenario_implications", SCENARIO_IMPLICATIONS_TEMPLATE.render(query=query)),
        ]
        base_case, alternatives, drivers, implications = await asyncio.gather(*tasks)
        return ServiceResult.ok({
            "base_case": base_case,
            "alternatives": alternatives,
            "drivers": drivers,
            "implications": implications,
        })
