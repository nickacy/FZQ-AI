# src/fzq_ai/civilization/civil_consensus.py
# V24-Final — Civilization Consensus Engine
"""
Civilization-level consensus & governance for FZQ-AI.

  Voting:     agents cast weighted votes on proposals
  Consensus:  compute majority/minority outcomes
  Governance: weighted decision-making with quorum checks

Integrated with: CivilizationEngine, CivilMemory, Orchestrator, Tracing.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class CivilizationConsensusEngine:
    """Civilization-level voting & consensus system."""

    def __init__(self):
        self._votes: Dict[str, Dict[str, float]] = {}   # proposal → {agent: value}
        self._weights: Dict[str, float] = {}             # agent → weight
        self._results: Dict[str, Any] = {}               # proposal → result
        self._history: List[Dict[str, Any]] = []

    # ── Agent weight ────────────────────────────────────────

    def set_weight(self, agent: str, weight: float) -> None:
        """Assign voting weight to an agent. Default is 1.0."""
        self._weights[agent] = max(0.0, weight)

    def get_weight(self, agent: str) -> float:
        return self._weights.get(agent, 1.0)

    # ── Vote ────────────────────────────────────────────────

    def vote(self, proposal: str, agent: str, value: Any) -> None:
        """Cast a weighted vote on a proposal."""
        self._votes.setdefault(proposal, {})[agent] = value
        self._log("vote_cast", proposal=proposal, agent=agent, value=value)

    # ── Compute ─────────────────────────────────────────────

    def compute(self, proposal: str, method: str = "majority") -> Dict[str, Any]:
        """
        Compute consensus for a proposal.

        Methods:
          majority   — value with most total weight wins
          unanimity  — all must agree
          average    — mean of numeric values
        """
        votes = self._votes.get(proposal, {})
        if not votes:
            return {"proposal": proposal, "result": None, "method": method, "status": "no_votes"}

        if method == "majority":
            tally: Dict[Any, float] = {}
            for agent, value in votes.items():
                w = self._weights.get(agent, 1.0)
                tally[value] = tally.get(value, 0) + w
            winner = max(tally, key=tally.get)
            total = sum(tally.values())
            confidence = tally[winner] / total if total else 0
            result = {
                "proposal": proposal, "winner": winner, "method": "majority",
                "confidence": round(confidence, 3), "tally": tally,
                "participants": len(votes),
            }

        elif method == "unanimity":
            unique = set(votes.values())
            result = {
                "proposal": proposal, "consensus": len(unique) == 1,
                "method": "unanimity", "values": list(unique),
                "participants": len(votes),
            }

        elif method == "average":
            numeric = [v for v in votes.values() if isinstance(v, (int, float))]
            avg = sum(numeric) / len(numeric) if numeric else None
            result = {
                "proposal": proposal, "average": avg, "method": "average",
                "participants": len(votes),
            }

        else:
            result = {"proposal": proposal, "error": f"Unknown method: {method}"}

        self._results[proposal] = result
        self._log("consensus_computed", **result)
        return result

    # ── Quorum ──────────────────────────────────────────────

    def has_quorum(self, proposal: str, threshold: float = 0.5) -> bool:
        """Check if enough agents voted on a proposal."""
        votes = self._votes.get(proposal, {})
        active = sum(1 for a in self._weights if self._weights[a] > 0)
        return len(votes) >= active * threshold if active else False

    # ── Snapshot ────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "proposals": list(self._votes.keys()),
            "results": dict(self._results),
            "weights": dict(self._weights),
            "active_agents": len([w for w in self._weights.values() if w > 0]),
        }

    # ── Logging ─────────────────────────────────────────────

    def _log(self, action: str, **meta: Any) -> None:
        self._history.append({"ts": time.time(), "action": action, **meta})
        if len(self._history) > 200:
            self._history = self._history[-100:]
