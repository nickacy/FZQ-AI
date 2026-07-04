"""Agent for zh_risk_scan — wraps the pipeline for autonomous task execution."""
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult


class RiskScanAgent(BaseAgent):
    name = "zh_risk_scan"

    def __init__(self) -> None:
        from fzq_ai.pipelines.registry import PipelineRegistry
        self._pipeline_name = "zh_risk_scan"

    async def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the zh_risk_scan pipeline with the agent context.

        V24-R2: civilization layer integration — remember input pre-call,
        snapshot + remember post-call, append civ trace to result.
        """
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
                civ.remember("risk_scan_input", repr(ctx.raw_input)[:200])
                civ_trace.append("civilization.remember.risk_scan")
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
                    civ.remember("risk_scan_status", str(result.get("status", "ok")) if isinstance(result, dict) else "ok")
                    civ_trace.append("civilization.remember.risk_scan_output")
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
