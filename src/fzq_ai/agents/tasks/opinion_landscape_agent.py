"""Agent for zh_opinion_landscape — wraps the pipeline for autonomous task execution."""
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult


class OpinionLandscapeAgent(BaseAgent):
    name = "zh_opinion_landscape"

    def __init__(self) -> None:
        from fzq_ai.pipelines.registry import PipelineRegistry
        self._pipeline_name = "zh_opinion_landscape"

    async def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the zh_opinion_landscape pipeline with the agent context."""
        from fzq_ai.pipelines.registry import PipelineRegistry

        trace: list[str] = []
        civ_trace: list[str] = []
        pipeline = PipelineRegistry.get(self._pipeline_name)
        trace.append("pipeline_loaded")

        # V24-R2: pre-civ remember
        civ = getattr(ctx, "civilization", None)
        if civ is None and hasattr(ctx, "metadata"):
            civ = ctx.metadata.get("civilization")
        if civ and hasattr(civ, "remember"):
            try:
                civ.remember("zh_opinion_landscape_input", repr(ctx.raw_input)[:200])
                civ_trace.append("civilization.remember.zh_opinion_landscape")
            except Exception:
                pass

        payload = {
            "event_topic": str(ctx.raw_input) if ctx.raw_input else "",
            "sources": ctx.metadata.get("sources", []),
        }
        if civ is not None:
            payload["civilization"] = civ

        try:
            result = await pipeline.run_async(**payload)
            trace.append("pipeline_executed")

            if civ and hasattr(civ, "remember"):
                try:
                    civ.remember("zh_opinion_landscape_status", str(result.get("status", "ok")) if isinstance(result, dict) else "ok")
                    civ_trace.append("civilization.remember.zh_opinion_landscape_output")
                except Exception:
                    pass

            return AgentResult(
                ok=True,
                data=result.model_dump() if hasattr(result, "model_dump") else result,
                warnings=[],
                trace=trace + civ_trace,
            )
        except Exception as e:
            trace.append(f"error: {e}")
            return AgentResult(
                ok=False,
                data=None,
                warnings=[str(e)],
                trace=trace + civ_trace,
            )
