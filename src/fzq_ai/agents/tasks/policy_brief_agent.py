# src/fzq_ai/agents/tasks/policy_brief_agent.py
"""Agent for zh_policy_brief — wraps the pipeline for autonomous task execution.

Note: the original 4-step implementation (GLM → DeepSeek struct-opt → minimax
validate → 豆包 format) referenced methods that don't exist on the current
LLMRouter / quality modules. V24 cleanup: simplify to the same pipeline-wrap
pattern as the other 3 task agents, deferring the full multi-model pipeline
to a follow-up iteration.
"""
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult


class PolicyBriefAgent(BaseAgent):
    name = "zh_policy_brief"

    def __init__(self) -> None:
        from fzq_ai.pipelines.registry import PipelineRegistry
        self._pipeline_name = "zh_policy_brief"

    def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the zh_policy_brief pipeline with the agent context."""
        import asyncio
        from fzq_ai.pipelines.registry import PipelineRegistry

        trace: list[str] = []
        pipeline = PipelineRegistry.get(self._pipeline_name)
        trace.append("pipeline_loaded")

        # Build payload from context
        payload = {
            "event_topic": str(ctx.raw_input) if ctx.raw_input else "",
            "sources": ctx.metadata.get("sources", []),
        }

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
            trace.append(f"error: {e}")
            return AgentResult(
                ok=False,
                data=None,
                warnings=[str(e)],
                trace=trace,
            )
