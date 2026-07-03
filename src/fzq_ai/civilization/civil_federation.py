# src/fzq_ai/civilization/civil_federation.py
# V24-Final — Civilization Federation Layer
"""
Federation governance across multiple civilizations.

  Members:   sovereign civilizations in the federation
  Vote:      inter-civilization weighted voting
  Decide:    binding federation directives
  Treaty:    formal agreements between civilizations
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class CivilizationFederation:
    """Federation of multiple FZQ-AI civilizations."""

    def __init__(self, name: str = "default"):
        self.name = name
        self._members: List[str] = []
        self._logs: List[Dict[str, Any]] = []
        self._consensus: Dict[str, Dict[str, float]] = {}
        self._directives: List[Dict[str, Any]] = []
        self._treaties: List[Dict[str, Any]] = []

    def add_member(self, civ_name: str) -> None:
        if civ_name not in self._members:
            self._members.append(civ_name)
        self._logs.append({"action": "add_member", "civ": civ_name, "ts": time.time()})

    @property
    def members(self) -> List[str]:
        return list(self._members)

    @property
    def member_count(self) -> int:
        return len(self._members)

    def vote(self, issue: str, options: List[str]) -> Dict[str, float]:
        tally = {opt: 0.0 for opt in options}
        for name in self._members:
            choice = options[hash(name + issue) % len(options)]
            tally[choice] += 1.0
        self._consensus[issue] = tally
        return dict(tally)

    def decide(self, issue: str) -> Optional[str]:
        votes = self._consensus.get(issue, {})
        if not votes:
            return None
        decision = max(votes, key=votes.get)
        self._directives.append({"issue": issue, "decision": decision, "ts": time.time()})
        return decision

    def treaty(self, title: str, terms: str, signatories: List[str]) -> Dict[str, Any]:
        entry = {"title": title, "terms": terms, "signatories": signatories, "ts": time.time()}
        self._treaties.append(entry)
        self._logs.append({"action": "treaty", "title": title, "ts": time.time()})
        return entry

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "members": list(self._members),
            "member_count": self.member_count,
            "consensus": dict(self._consensus),
            "directives": list(self._directives[-10:]),
            "treaties": list(self._treaties[-5:]),
            "logs": list(self._logs[-10:]),
        }
