from fzq_ai.pipelines.refinement_pipeline import MultiModelRefinementPipeline

class ChinaIntelPipeline:

    def __init__(self):
        self.refiner = MultiModelRefinementPipeline()

    async def run(self, text: str):
        brief = await self.refiner.run("zh_policy_brief", text)
        opinion = await self.refiner.run("zh_opinion_landscape", text)

        return {
            "policy_brief": brief,
            "opinion_landscape": opinion,
        }
