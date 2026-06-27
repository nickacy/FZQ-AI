"""Agent for zh_multisource_merge — wraps the pipeline for autonomous task execution."""
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult


class MultisourceMergeAgent(BaseAgent):
    name = "zh_multisource_merge"

    def __init__(self) -> None:
        from fzq_ai.pipelines.registry import PipelineRegistry
        self._pipeline_name = "zh_multisource_merge"

    def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the zh_multisource_merge pipeline with the agent context."""
        import asyncio
        from fzq_ai.pipelines.registry import PipelineRegistry

        trace: list[str] = []
        pipeline = PipelineRegistry.get(self._pipeline_name)
        trace.append("pipeline_loaded")

        # Build payload from context
        payload = {{
            "event_topic": str(ctx.raw_input) if ctx.raw_input else "",
            "sources": ctx.metadata.get("sources", []),
        }}

        try:
            result = asyncio.run(pipeline.run_async(**payload))
            trace.append("pipeline_executed")
            return AgentResult(
                ok=True,
                data=result.model_dump() if hasattr(result, "model_dump") else result,
                warnings=[],
                trace=trace,
            )
        except Exception as e:
            trace.append(f"error: {{e}}")
            return AgentResult(
                ok=False,
                data=None,
                warnings=[str(e)],
                trace=trace,
            )
