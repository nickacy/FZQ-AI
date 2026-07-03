# V24-Final — Civilization Federation Council V2
"""Multi-round debate, multi-dimension voting, multi-level decisions."""
from typing import List, Dict, Any
import time as _t

class CivilizationFederationCouncilV2:
    def __init__(self):
        self.members: Dict[str, Any] = {}
        self.debate_rounds: List[Dict] = []
        self.multi_votes: List[Dict] = []
        self.decisions: List[Dict] = []

    def add_member(self, name: str, snapshot: Any = None) -> None:
        self.members[name] = snapshot or {}

    def debate_round(self, issue: str) -> Dict:
        r = {name: f"[{name}] v2 position on {issue}" for name in self.members}
        self.debate_rounds.append({"issue": issue, "ts": _t.time(), "round": r})
        return r

    def multi_vote(self, issue: str, dimensions: List[str]) -> Dict:
        result = {}
        for dim in dimensions:
            result[dim] = {"approve": 0, "reject": 0, "revise": 0}
            for name in self.members:
                choice = ["approve","reject","revise"][hash(name+dim) % 3]
                result[dim][choice] += 1
        self.multi_votes.append({"issue": issue, "ts": _t.time(), "votes": result})
        return result

    def decide(self, issue: str) -> Dict:
        last = self.multi_votes[-1].get("votes", {}) if self.multi_votes else {}
        decision = {dim: max(votes,key=votes.get) for dim, votes in last.items()}
        self.decisions.append({"issue": issue, "ts": _t.time(), "decision": decision})
        return decision

    def snapshot(self) -> dict:
        return {"members": list(self.members.keys()), "debates": list(self.debate_rounds[-5:]), "votes": list(self.multi_votes[-5:]), "decisions": list(self.decisions[-5:])}
