from fzq_ai.pipelines.refinement_pipeline import MultiModelRefinementPipeline
from fzq_ai.llm.router import LLMRouter

class DailyReportPipeline:

    def __init__(self):
        self.refiner = MultiModelRefinementPipeline()
        self.llm = LLMRouter()

    async def run(self, text: str):
        overview = await self.refiner.run("daily_exec_overview", text)
        outlook = await self.refiner.run("daily_outlook", text)

        # 非关键段落仍走智能调度
        top_stories = await self.llm.route("daily_top_stories", text)

        return {
            "overview": overview,
            "top_stories": top_stories,
            "outlook": outlook,
        }
