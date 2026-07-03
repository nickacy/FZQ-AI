# src/fzq_ai/utils/reflection.py
# V24-Final — Agent Reflection Engine
"""
Reflection system for FZQ-AI agents.

  Instant reflection:  after each execution → evaluate quality
  Deep reflection:     periodic → meta-analysis of past reflections
  Feedback loop:       reflections → influence planning, goals, memory, personality

Integrated with: PromptEngine, PlanningEngine, Goals, Memory, Personality, Tracing.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class ReflectionEngine:
    """Central reflection store for all agents."""

    def __init__(self):
        self._reflections: Dict[str, List[Dict[str, Any]]] = {}  # agent → [entry, ...]

    # ── Core API ─────────────────────────────────────────────

    def add(self, agent: str, text: str, score: Optional[float] = None, kind: str = "instant") -> None:
        entry = {
            "text": text,
            "score": score,
            "kind": kind,
            "timestamp": time.time(),
        }
        self._reflections.setdefault(agent, []).append(entry)
        self._log("reflection_added", agent, kind=kind, score=score)

    def get(self, agent: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._reflections.get(agent, [])[-limit:]

    def last(self, agent: str) -> Optional[Dict[str, Any]]:
        entries = self._reflections.get(agent, [])
        return entries[-1] if entries else None

    def count(self, agent: str) -> int:
        return len(self._reflections.get(agent, []))

    def clear(self, agent: str) -> None:
        self._reflections.pop(agent, None)

    # ── Feedback helpers ─────────────────────────────────────

    def should_deep_reflect(self, agent: str) -> bool:
        """Trigger deep reflection every N instant reflections."""
        count = self.count(agent)
        return count > 0 and count % 5 == 0

    def average_score(self, agent: str) -> Optional[float]:
        scores = [e["score"] for e in self._reflections.get(agent, []) if e.get("score") is not None]
        return sum(scores) / len(scores) if scores else None

    def summary(self, agent: str) -> str:
        """Human-readable summary of recent reflections."""
        entries = self.get(agent, limit=5)
        if not entries:
            return "暂无反思记录。"
        avg = self.average_score(agent)
        lines = [f"反思次数：{self.count(agent)}"]
        if avg:
            lines.append(f"平均质量分：{avg:.2f}")
        lines.append("最近反思：")
        for e in entries[-3:]:
            lines.append(f"  [{e['kind']}] {e['text'][:80]}")
        return "\n".join(lines)

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self, agent: str) -> Dict[str, Any]:
        return {
            "reflections": self.get(agent),
            "count": self.count(agent),
            "average_score": self.average_score(agent),
            "last": self.last(agent),
        }

    # ── Logging ──────────────────────────────────────────────

    def _log(self, action: str, agent: str, **meta: Any) -> None:
        from fzq_ai.utils.logger import log_event
        log_event("reflection." + action, agent=agent, **meta)


# ── Global instance ──────────────────────────────────────────

global_reflector = ReflectionEngine()
