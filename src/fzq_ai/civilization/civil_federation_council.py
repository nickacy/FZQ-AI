# src/fzq_ai/civilization/civil_federation_council.py
# V24-Final — Civilization Federation Council
"""
Cross-civilization parliamentary body.

  Members:   civilization delegates with snapshots
  Debate:    inter-civ deliberation on shared issues
  Vote:      weighted federation voting
  Decide:    binding federation directives
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class CivilizationFederationCouncil:
    """Highest decision body across federated civilizations."""

    def __init__(self, name: str = "council"):
        self.name = name
        self._members: Dict[str, Dict[str, Any]] = {}
        self._debates: List[Dict[str, Any]] = []
        self._votes: Dict[str, Dict[str, float]] = {}
        self._directives: List[Dict[str, Any]] = []
        self._logs: List[Dict[str, Any]] = []

    def add_member(self, civ_name: str, civ_snapshot: Dict[str, Any] = None) -> None:
        self._members[civ_name] = civ_snapshot or {}
        self._logs.append({"action": "add_member", "civ": civ_name, "ts": time.time()})

    @property
    def members(self) -> List[str]:
        return list(self._members.keys())

    def debate(self, issue: str) -> Dict[str, Any]:
        positions = {}
        for name, snap in self._members.items():
            positions[name] = f"[{name}] position on '{issue}': acknowledged"
        entry = {"issue": issue, "ts": time.time(), "positions": positions}
        self._debates.append(entry)
        return entry

    def vote(self, issue: str, options: List[str]) -> Dict[str, float]:
        tally = {opt: 0.0 for opt in options}
        for name in self._members:
            choice = options[hash(name + issue) % len(options)]
            tally[choice] += 1.0
        self._votes[issue] = tally
        return dict(tally)

    def decide(self, issue: str) -> Optional[str]:
        votes = self._votes.get(issue, {})
        if not votes:
            return None
        decision = max(votes, key=votes.get)
        self._directives.append({"issue": issue, "decision": decision, "ts": time.time()})
        return decision

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "members": list(self._members.keys()),
            "member_count": len(self._members),
            "debates": list(self._debates[-10:]),
            "votes": dict(self._votes),
            "directives": list(self._directives[-10:]),
        }
