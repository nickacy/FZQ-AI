# src/fzq_ai/agents/news_agent_v24.py
# V24 — NewsAgent (async, with civilization integration)

from __future__ import annotations
import logging
from typing import Any, Dict, List
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult
_logger = logging.getLogger("fzq_ai.news_agent_v24")


class NewsAgentV24(BaseAgent):
    """V24 NewsAgent — async run() with civilization integration.

    V24-R2: uses async `run()` (inherits BaseAgent) and writes to
    civilization memory on entry/exit. Compatible with `BaseAgent.run()`
    default plan→execute→reflect→heal flow.
    """

    def __init__(self):
        super().__init__(name="NewsAgentV24")

    def plan(self, ctx: AgentContext) -> Dict[str, Any]:
        return {
            "raw": ctx.raw_input,
            "languages": ctx.languages,
            "focus_regions": ctx.focus_regions,
            "metadata": ctx.metadata,
        }

    def route(self, plan: Dict[str, Any]) -> str:
        if "zh" in plan.get("languages", []):
            return "glm-4"
        return "deepseek-chat"

    def execute(self, model: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from fzq_ai.orchestrator.blackboard import Blackboard
            import time
            Blackboard.write(f"agents.{self.name}.input", {"payload": repr(plan), "ts": time.time()})
            summary = f"[{model}] {plan.get('raw', '')[:80]}..."
            result = {"summary": summary}
            Blackboard.write(f"agents.{self.name}.output", {"result": result, "ts": time.time()})
        except Exception:
            summary = f"[{model}] {plan.get('raw', '')[:80]}..."
            result = {"summary": summary}
        return result

    def evaluate(self, result: Dict[str, Any]) -> float:
        if not result or "summary" not in result:
            return 0.0
        return 0.85

    def reflect(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result["reflection"] = "ok"
        return result

    def heal(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result["healed"] = True
        return result

    def fallback(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {"summary": "fallback summary"}

    def retry(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {"summary": "retry summary"}

    def auto_select_model(self, plan: Dict[str, Any]) -> str:
        return self.route(plan)

    # ============================================================
    # V24-R2: async run() override with civilization integration
    # ============================================================
    async def run(self, ctx: AgentContext) -> AgentResult:
        civ_trace: List[str] = []

        # 1. Pre-civ: remember input
        civ = getattr(ctx, "civilization", None)
        if civ is None and hasattr(ctx, "metadata"):
            civ = ctx.metadata.get("civilization")
        if civ and hasattr(civ, "remember"):
            try:
                # V24-R2: store raw_input as-is (string-friendly), cap at 200 chars
                _inp = ctx.raw_input if isinstance(ctx.raw_input, str) else str(ctx.raw_input)
                civ.remember("news_agent_input", _inp[:200])
                civ_trace.append("civilization.remember.news_agent")
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        # 2. Default BaseAgent run (plan → route → execute → reflect → heal)
        result = await super().run(ctx)

        # 3. Post-civ: remember output + trace
        if civ and hasattr(civ, "remember"):
            try:
                _out = result.data if isinstance(result.data, str) else str(result.data) if result.data else ""
                civ.remember("news_agent_output", _out[:200])
                civ_trace.append("civilization.remember.news_agent_output")
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        # 4. Append civ trace to result
        result.trace = (result.trace or []) + civ_trace
        return result
