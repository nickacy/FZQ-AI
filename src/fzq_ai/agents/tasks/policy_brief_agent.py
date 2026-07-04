import logging
# src/fzq_ai/agents/tasks/policy_brief_agent.py
"""Agent for zh_policy_brief — wraps the pipeline for autonomous task execution.

Note: the original 4-step implementation (GLM → DeepSeek struct-opt → minimax
validate → 豆包 format) referenced methods that don't exist on the current
LLMRouter / quality modules. V24 cleanup: simplify to the same pipeline-wrap
pattern as the other 3 task agents, deferring the full multi-model pipeline
to a follow-up iteration.
"""
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult
_logger = logging.getLogger("fzq_ai.policy_brief_agent")


class PolicyBriefAgent(BaseAgent):
    name = "zh_policy_brief"

    def __init__(self) -> None:
        from fzq_ai.pipelines.registry import PipelineRegistry
        self._pipeline_name = "zh_policy_brief"

    async def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the zh_policy_brief pipeline with the agent context.

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
                civ.remember("policy_brief_input", repr(ctx.raw_input)[:200])
                civ_trace.append("civilization.remember.policy_brief")
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        # Build payload from context
        payload = {
            "event_topic": str(ctx.raw_input) if ctx.raw_input else "",
            "sources": ctx.metadata.get("sources", []),
        }
        # V24-R2: forward civilization into pipeline via ctx-shaped payload
        if civ is not None:
            payload["civilization"] = civ

        try:
            result = await pipeline.run_async(**payload)
            trace.append("pipeline_executed")

            # V24-R2: post-civ remember + snapshot
            if civ and hasattr(civ, "remember"):
                try:
                    civ.remember("policy_brief_status", str(result.get("status", "ok")) if isinstance(result, dict) else "ok")
                    civ_trace.append("civilization.remember.policy_brief_output")
                except Exception:
                    _logger.warning("Suppressed error", exc_info=True)

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
