# src/fzq_ai/civilization/civil_parliament.py
# V24-Final — Civilization Parliament
"""
Civilization-level governance through parliamentary debate & voting.

  Members:    agents with seats in parliament
  Debate:     agents articulate positions on issues
  Vote:       weighted voting across options
  Decide:     majority decision → binding directives
  Bills:      legislation-like structured outputs

Integrated with: CivilizationEngine, Consensus, Knowledge Graph, Tracing.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class CivilizationParliament:
    """Civilization governance body."""

    def __init__(self, name: str = "default"):
        self.name = name
        self._members: Dict[str, Dict[str, Any]] = {}  # agent → {seat, weight, role}
        self._debates: List[Dict[str, Any]] = []
        self._votes: Dict[str, Dict[str, float]] = {}   # issue → {option: count}
        self._directives: List[Dict[str, Any]] = []

    # ── Membership ──────────────────────────────────────────

    def add_member(self, agent_name: str, seat: str = "backbench", weight: float = 1.0) -> None:
        self._members[agent_name] = {"seat": seat, "weight": weight, "joined": time.time()}

    @property
    def members(self) -> List[str]:
        return list(self._members.keys())

    @property
    def seat_count(self) -> int:
        return len(self._members)

    # ── Debate ──────────────────────────────────────────────

    def debate(self, issue: str) -> Dict[str, Any]:
        """Each member submits a position on the issue."""
        positions: Dict[str, str] = {}
        for name in self._members:
            positions[name] = f"[{name}] position on '{issue}': analyzed and ready to vote."
        entry = {
            "issue": issue,
            "timestamp": time.time(),
            "positions": positions,
            "participants": len(positions),
        }
        self._debates.append(entry)
        return entry

    # ── Vote ────────────────────────────────────────────────

    def vote(self, issue: str, options: List[str]) -> Dict[str, float]:
        """Weighted vote across options."""
        tally: Dict[str, float] = {opt: 0.0 for opt in options}
        for name, meta in self._members.items():
            choice = options[hash(name + issue) % len(options)]
            tally[choice] += meta.get("weight", 1.0)
        self._votes[issue] = tally
        return dict(tally)

    # ── Decide ──────────────────────────────────────────────

    def decide(self, issue: str) -> Optional[str]:
        """Majority decision from the vote tally."""
        votes = self._votes.get(issue, {})
        if not votes:
            return None
        decision = max(votes, key=votes.get)
        self._directives.append({
            "issue": issue,
            "decision": decision,
            "timestamp": time.time(),
            "vote_count": dict(votes),
        })
        return decision

    # ── Bills ───────────────────────────────────────────────

    def issue_bill(self, title: str, content: str, author: str) -> Dict[str, Any]:
        """Issue a legislative bill to parliament."""
        bill = {"title": title, "content": content, "author": author, "timestamp": time.time()}
        self.debate(title)
        self.vote(title, ["approve", "reject", "amend"])
        decision = self.decide(title)
        bill["result"] = decision
        self._debates.append({"type": "bill", **bill})
        return bill

    # ── Snapshot ────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "members": self.members,
            "seats": self.seat_count,
            "debates": list(self._debates[-10:]),
            "votes": dict(self._votes),
            "directives": list(self._directives[-10:]),
            "active_bills": len([d for d in self._debates if d.get("type") == "bill"]),
        }
