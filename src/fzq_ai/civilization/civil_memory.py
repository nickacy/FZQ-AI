# src/fzq_ai/civilization/civil_memory.py
# V24-Final — Civilization Memory Engine
"""
Civilization-level collective memory for FZQ-AI.

  Events:      civil-level event log
  Knowledge:   shared knowledge base (key → value)
  Goals:       civil objectives
  Planning:    civil task decomposition
  Consensus:   parliamentary decisions
  Collaboration: agent interaction graph snapshots

Integrated with: CivilizationEngine, Orchestrator, Tracing, Monitoring.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class CivilizationMemoryEngine:
    """Civilization-wide collective memory."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.knowledge: Dict[str, Any] = {}
        self.goals: Dict[str, Any] = {}
        self.planning: Dict[str, Any] = {}
        self.consensus: Dict[str, Any] = {}
        self.collaboration_snapshots: List[Dict[str, Any]] = []

    # ── Event log ───────────────────────────────────────────

    def record_event(self, event: str, agent: str = "", **meta: Any) -> None:
        self.events.append({
            "timestamp": time.time(), "event": event, "agent": agent, **meta,
        })
        if len(self.events) > 500:
            self.events = self.events[-250:]

    # ── Knowledge ───────────────────────────────────────────

    def store_knowledge(self, key: str, value: Any) -> None:
        self.knowledge[key] = value

    def recall_knowledge(self, key: str, default: Any = None) -> Any:
        return self.knowledge.get(key, default)

    # ── Goals / Planning / Consensus ────────────────────────

    def set_goal(self, key: str, value: Any) -> None:
        self.goals[key] = value

    def set_plan(self, key: str, value: Any) -> None:
        self.planning[key] = value

    def set_consensus(self, key: str, value: Any) -> None:
        self.consensus[key] = value

    def build_consensus(self, agent_states: Dict[str, str]) -> str:
        """Parliamentary voting: majority state wins."""
        votes: Dict[str, int] = {}
        for state in agent_states.values():
            votes[state] = votes.get(state, 0) + 1
        winner = max(votes, key=votes.get) if votes else "UNKNOWN"
        self.set_consensus("state_consensus", winner)
        self.set_consensus("vote_distribution", votes)
        return winner

    # ── Collaboration snapshot ───────────────────────────────

    def snapshot_collaboration(self, graph: Dict[str, List[str]]) -> None:
        self.collaboration_snapshots.append({
            "timestamp": time.time(),
            "graph": {k: list(v) for k, v in graph.items()},
        })

    # ── Full snapshot ────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "events": list(self.events[-50:]),
            "knowledge_keys": list(self.knowledge.keys()),
            "goals_keys": list(self.goals.keys()),
            "planning_keys": list(self.planning.keys()),
            "consensus": dict(self.consensus),
            "collaboration_snapshots": list(self.collaboration_snapshots[-5:]),
            "total_events": len(self.events),
        }
