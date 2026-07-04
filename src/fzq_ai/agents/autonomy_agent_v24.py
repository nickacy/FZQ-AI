# src/fzq_ai/agents/autonomy_agent_v24.py
# V24 — AutonomyAgent (wired into unified_orchestrator_v24)

from __future__ import annotations
from typing import Any, Dict, List

from fzq_ai.agents.base import AgentContext, AgentResult


class AutonomyAgentV24:
    """V24 Autonomy Agent — plan / route / execute / reflect / heal loop.

    V24-R2: implements the standard `async def run(ctx: AgentContext) -> AgentResult`
    signature so it can integrate with the registry and civilization layer,
    matching the other V24 agents (news_center, news_agent, task agents).
    """

    name = "autonomy"

    def __init__(self) -> None:
        self.civ_trace: List[str] = []

    def plan(self, ctx: AgentContext) -> Dict[str, Any]:
        return {"raw_input": ctx.raw_input, "plan": "decomposed"}

    def route(self, plan: Dict[str, Any]) -> str:
        return "deepseek-chat"

    async def execute(self, model: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {"summary": f"[{model}] autonomous execution result for: {plan.get('raw_input', '')[:80]}"}

    def reflect(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result["reflection"] = "ok"
        return result

    def heal(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result["healed"] = True
        return result

    # ============================================================
    # V24-R2: async run() with civilization integration
    # ============================================================
    async def run(self, ctx: AgentContext) -> AgentResult:
        self.civ_trace = []
        trace: List[str] = ["autonomy_start"]

        # 1. Plan + route + execute (sync steps chained)
        plan = self.plan(ctx)
        trace.append("autonomy_plan")
        model = self.route(plan)
        trace.append(f"autonomy_route:{model}")
        raw = await self.execute(model, plan)
        trace.append("autonomy_execute")
        raw = self.reflect(raw)
        raw = self.heal(raw)
        trace.append("autonomy_heal")

        # 2. Civilization: remember and enrich
        civ = getattr(ctx, "civilization", None)
        if civ is None and hasattr(ctx, "metadata"):
            civ = ctx.metadata.get("civilization")
        if civ and hasattr(civ, "remember"):
            try:
                civ.remember("autonomy_input", repr(ctx.raw_input)[:200])
                civ.remember("autonomy_model", model)
                self.civ_trace.append("civilization.remember.autonomy")
            except Exception:
                pass

        return AgentResult(
            ok=True,
            data={"result": raw, "model": model, "plan": plan},
            warnings=[],
            trace=trace + self.civ_trace,
        )
