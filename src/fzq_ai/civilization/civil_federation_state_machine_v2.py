# V24-Final — Civilization Federation State Machine V2
"""Multi-level transitions, dependency graph, stability + repair."""
from typing import List, Dict, Any
import time as _t

class CivilizationFederationStateMachineV2:
    def __init__(self):
        self.states: List[str] = []
        self.transitions: List[Dict] = []
        self.deps: List[Dict] = []
        self.stability: List[Dict] = []
        self.repairs: List[Dict] = []

    def add_state(self, state: str) -> str:
        self.states.append(state)
        return state

    def transition(self, frm: str, to: str, reason: str = "") -> Dict:
        t = {"from": frm, "to": to, "reason": reason, "ts": _t.time()}
        self.transitions.append(t)
        return t

    def build_dependency(self, frm: str, to: str) -> Dict:
        d = {"from": frm, "to": to, "ts": _t.time()}
        self.deps.append(d)
        return d

    def assess(self) -> Dict:
        s = {"overall": "stable", "governance": "stable", "intelligence": "improving", "protocol": "aligned", "bridge": "active"}
        self.stability.append(s)
        return s

    def repair(self) -> Dict:
        r = {"governance": "increase consensus", "protocol": "optimize sync", "bridge": "reinforce"}
        self.repairs.append(r)
        return r

    def snapshot(self) -> dict:
        return {"states": list(self.states), "transitions": list(self.transitions[-20:]), "deps": list(self.deps[-10:]), "stability": list(self.stability[-5:]), "repairs": list(self.repairs[-5:])}
