# src/fzq_ai/utils/planning.py
# V24-Final — Agent Planning Engine
"""
Hierarchical planning system for FZQ-AI agents.

  Steps: ordered action list (per-request, per-agent)
  Plan:  high-level decomposition + low-level action steps

Integrated with: PromptEngine, Goals, Personality, Orchestrator, Tracing.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class PlanningEngine:
    """Central planning store for all agents."""

    def __init__(self):
        self._plans: Dict[str, List[str]] = {}        # agent → [step, ...]
        self._meta: Dict[str, Dict[str, Any]] = {}    # agent → {intent, created_at, ...}
        self._history: List[Dict[str, Any]] = []      # completed plans

    # ── Plan lifecycle ──────────────────────────────────────

    def create(self, agent: str, intent: str, steps: List[str]) -> List[str]:
        """Create a new plan for an agent."""
        self._plans[agent] = steps
        self._meta[agent] = {
            "intent": intent,
            "created_at": time.time(),
            "total_steps": len(steps),
            "completed": 0,
        }
        self._log("plan_created", agent, steps=steps)
        return steps

    def get(self, agent: str) -> List[str]:
        """Get the current plan for an agent."""
        return list(self._plans.get(agent, []))

    def next_step(self, agent: str) -> Optional[str]:
        """Get the next pending step (first uncompleted)."""
        steps = self._plans.get(agent, [])
        completed = self._meta.get(agent, {}).get("completed", 0)
        if completed < len(steps):
            return steps[completed]
        return None

    def mark_done(self, agent: str) -> None:
        """Mark the current step as completed."""
        if agent in self._meta:
            self._meta[agent]["completed"] = min(
                self._meta[agent].get("completed", 0) + 1,
                len(self._plans.get(agent, [])),
            )

    def is_complete(self, agent: str) -> bool:
        """Check if all steps are done."""
        steps = self._plans.get(agent, [])
        completed = self._meta.get(agent, {}).get("completed", 0)
        return completed >= len(steps) and len(steps) > 0

    def clear(self, agent: str) -> None:
        """Archive and clear a plan."""
        if agent in self._plans:
            self._history.append({
                "agent": agent,
                "plan": list(self._plans[agent]),
                "meta": dict(self._meta.get(agent, {})),
            })
            self._plans.pop(agent, None)
            self._meta.pop(agent, None)
            self._log("plan_archived", agent)

    # ── Decomposition helpers ────────────────────────────────

    @staticmethod
    def decompose(intent: str, num_steps: int = 4) -> List[str]:
        """Simple rule-based plan decomposition (LLM-free fallback)."""
        patterns = {
            "风险": ["识别风险因素", "评估风险等级", "分析影响范围", "制定应对方案"],
            "政策": ["梳理政策要点", "分析影响", "对比国际做法", "给出建议"],
            "新闻": ["收集相关新闻", "提取关键信息", "分析趋势", "生成摘要"],
            "舆情": ["采集舆情数据", "分析情绪倾向", "识别关键话题", "输出报告"],
            "合并": ["获取多源信息", "去重清洗", "融合分析", "输出统一报告"],
        }
        for keyword, steps in patterns.items():
            if keyword in intent:
                return steps[:num_steps]
        return ["分析输入", "提取关键信息", "生成分析", "输出结果"][:num_steps]

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self, agent: str) -> Dict[str, Any]:
        return {
            "plan": self.get(agent),
            "meta": dict(self._meta.get(agent, {})),
            "is_complete": self.is_complete(agent),
            "next_step": self.next_step(agent),
        }

    # ── Prompt template ──────────────────────────────────────

    @staticmethod
    def plan_prompt(intent: str) -> str:
        """Build a prompt that asks an LLM to generate a plan."""
        return (
            "将以下任务分解为 3–5 个具体执行步骤，每行一个步骤：\n"
            f"任务：{intent}\n\n"
            "步骤："
        )

    # ── Logging ──────────────────────────────────────────────

    def _log(self, action: str, agent: str, **meta: Any) -> None:
        from fzq_ai.utils.logger import log_event
        log_event("planning." + action, agent=agent, **meta)


# ── Global instance ──────────────────────────────────────────

global_planner = PlanningEngine()
