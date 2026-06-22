from fzq_ai.pipelines.refinement_pipeline import MultiModelRefinementPipeline

class ScenarioPipeline:

    def __init__(self):
        self.refiner = MultiModelRefinementPipeline()

    async def run(self, text: str):
        base = await self.refiner.run("scenario_base_case", text)
        alt = await self.refiner.run("scenario_alternatives", text)
        drivers = await self.refiner.run("scenario_drivers", text)
        implications = await self.refiner.run("scenario_implications", text)

        return {
            "base_case": base,
            "alternatives": alt,
            "drivers": drivers,
            "implications": implications,
        }
