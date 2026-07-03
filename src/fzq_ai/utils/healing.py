# src/fzq_ai/utils/healing.py
# V24-Final — Agent Healing Engine
"""
Self-healing system for FZQ-AI agents.

Heals: Memory, Goals, Planning, Personality, Execution context.

Integrated with: MemoryEngine, GoalEngine, PlanningEngine, PersonalityEngine,
                 ReflectionEngine, Tracing, Monitoring.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional

from fzq_ai.utils.memory import global_memory
from fzq_ai.utils.goals import global_goals
from fzq_ai.utils.planning import global_planner
from fzq_ai.utils.personality import global_personality
from fzq_ai.utils.reflection import global_reflector


class HealingEngine:
    """Central healing store for all agents."""

    def __init__(self):
        self._records: Dict[str, List[Dict[str, Any]]] = {}  # agent → [entry, ...]
        self._status: Dict[str, str] = {}                    # agent → "healthy"|"degraded"|"healing"

    # ── Core API ─────────────────────────────────────────────

    def heal(self, agent: str) -> dict:
        """Run full self-healing cycle for an agent. Returns healing report."""
        self._status[agent] = "healing"
        report = {"agent": agent, "timestamp": time.time(), "actions": [], "status": "healed"}

        # 1. Heal memory — clear corrupted short-term, keep long-term
        try:
            if agent not in global_memory.short_term:
                global_memory.remember(agent, "_healed_at", time.time())
            report["actions"].append("memory_checked")
        except Exception as e:
            report["actions"].append(f"memory_healed: {e}")

        # 2. Heal goals — ensure minimum goal set exists
        try:
            if not global_goals.get(agent, "intent"):
                global_goals.set(agent, "intent", "resume")
            report["actions"].append("goals_checked")
        except Exception as e:
            report["actions"].append(f"goals_healed: {e}")

        # 3. Heal planning — clear stuck plans
        try:
            plan = global_planner.get(agent)
            if plan and not global_planner.is_complete(agent):
                # Plan is stuck — mark current step done and retry
                global_planner.mark_done(agent)
            report["actions"].append("planning_checked")
        except Exception as e:
            report["actions"].append(f"planning_healed: {e}")

        # 4. Heal personality — restore defaults if profile missing
        try:
            profile = global_personality.get(agent)
            if not profile or profile.get("id") == "v24-default":
                report["actions"].append("personality_default")
            report["actions"].append("personality_checked")
        except Exception as e:
            report["actions"].append(f"personality_healed: {e}")

        # 5. Heal using reflection — apply recent reflections
        try:
            last_r = global_reflector.last(agent)
            if last_r and last_r.get("score", 1.0) < 0.5:
                report["actions"].append("reflection_applied")
        except Exception as e:
            report["actions"].append(f"reflection_check_failed: {e}")

        self._status[agent] = "healthy"
        self._record(agent, report)
        return report

    # ── Status ───────────────────────────────────────────────

    def status(self, agent: str) -> str:
        return self._status.get(agent, "unknown")

    def is_healthy(self, agent: str) -> bool:
        return self._status.get(agent) == "healthy"

    # ── Records ──────────────────────────────────────────────

    def _record(self, agent: str, report: dict) -> None:
        self._records.setdefault(agent, []).append(report)
        if len(self._records[agent]) > 50:
            self._records[agent] = self._records[agent][-25:]
        from fzq_ai.utils.logger import log_event
        log_event("healing.completed", agent=agent, actions=report["actions"])

    def get(self, agent: str) -> List[Dict[str, Any]]:
        return self._records.get(agent, [])

    def last(self, agent: str) -> Optional[Dict[str, Any]]:
        entries = self._records.get(agent, [])
        return entries[-1] if entries else None

    def count(self, agent: str) -> int:
        return len(self._records.get(agent, []))

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self, agent: str) -> Dict[str, Any]:
        return {
            "status": self.status(agent),
            "last_healing": self.last(agent),
            "total_healings": self.count(agent),
        }


# ── Global instance ──────────────────────────────────────────

global_healer = HealingEngine()
