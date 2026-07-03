# src/fzq_ai/agents/news_agent_v24.py
# V24 — NewsAgent (sync version — compatible with BaseAgent.run())

from __future__ import annotations
from typing import Any, Dict
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult


class NewsAgentV24(BaseAgent):
    """V24 NewsAgent — all methods sync for BaseAgent compatibility."""

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
