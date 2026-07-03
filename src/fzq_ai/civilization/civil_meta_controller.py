# src/fzq_ai/civilization/civil_meta_controller.py
# V24-Final — Civilization Meta-Controller
"""
Highest-level civilization controller for FZQ-AI.

  Analyze:    snapshot all civilization subsystems
  Prioritize: generate civil priorities from evolution score
  Direct:     issue binding civil directives from parliament
  Govern:     self-management, self-correction, self-evolution control

Integrated with: all Civilization modules, Orchestrator, Tracing.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class CivilizationMetaController:
    """Top-level civilization governance & control."""

    def __init__(self, civ):
        self.civ = civ
        self._logs: List[Dict[str, Any]] = []
        self._directives: List[Dict[str, Any]] = []
        self._priorities: List[str] = []
        self._cycle: int = 0

    # ── Analyze ─────────────────────────────────────────────

    def analyze(self) -> Dict[str, Any]:
        """Full civilization health snapshot."""
        self._cycle += 1
        snapshot = {
            "cycle": self._cycle,
            "timestamp": time.time(),
            "memory": self._safe_snapshot("memory"),
            "knowledge_graph": self._safe_snapshot("knowledge_graph"),
            "consensus": self._safe_snapshot("consensus_engine"),
            "parliament": self._safe_snapshot("parliament"),
            "evolution": self._safe_snapshot("evolution"),
        }
        self._logs.append(snapshot)
        return snapshot

    # ── Prioritize ──────────────────────────────────────────

    def generate_priority(self) -> str:
        """Generate civilization priority based on evolution score."""
        evo = getattr(getattr(self.civ, 'evolution', None), '_history', [])
        last_score = evo[-1].get("evolution_score", 0) if evo else 0
        if last_score > 10:
            priority = "high"
        elif last_score > 3:
            priority = "medium"
        else:
            priority = "low"
        self._priorities.append(priority)
        return priority

    # ── Direct ──────────────────────────────────────────────

    def generate_directive(self) -> Dict[str, Any]:
        """Issue a civil directive based on parliament output."""
        parliament = getattr(self.civ, 'parliament', None)
        directives = getattr(parliament, '_directives', []) if parliament else []
        last = directives[-1] if directives else {"global": "continue"}
        self._directives.append(last)
        return last

    # ── Govern (self-management loop) ────────────────────────

    def govern(self) -> Dict[str, Any]:
        """Run one full governance cycle."""
        analysis = self.analyze()
        priority = self.generate_priority()
        directive = self.generate_directive()

        if hasattr(self.civ, 'memory'):
            self.civ.memory.record_event(
                "meta_controller.govern", cycle=self._cycle,
                priority=priority, directive=str(directive)[:100])

        return {
            "cycle": self._cycle,
            "analysis": {k: "ok" if v else "missing" for k, v in analysis.items()},
            "priority": priority,
            "directive": directive,
        }

    # ── Helpers ─────────────────────────────────────────────

    def _safe_snapshot(self, attr: str) -> Optional[Dict[str, Any]]:
        obj = getattr(self.civ, attr, None)
        if obj and hasattr(obj, 'snapshot'):
            return obj.snapshot()
        return None

    # ── Snapshot ────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "cycle": self._cycle,
            "logs": list(self._logs[-10:]),
            "directives": list(self._directives[-10:]),
            "priorities": list(self._priorities[-10:]),
            "current_priority": self._priorities[-1] if self._priorities else "unknown",
        }
