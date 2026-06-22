from fzq_ai.pipelines.refinement_pipeline import MultiModelRefinementPipeline

class RiskPipeline:

    def __init__(self):
        self.refiner = MultiModelRefinementPipeline()

    async def run(self, text: str):
        summary = await self.refiner.run("risk_summary", text)
        forecast = await self.refiner.run("risk_forecast", text)

        return {
            "summary": summary,
            "forecast": forecast,
        }
