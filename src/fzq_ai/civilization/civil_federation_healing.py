# src/fzq_ai/civilization/civil_federation_healing.py
# V24-Final — Civilization Federation Healing
"""Self-healing system for the civilization federation."""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationHealing:
    """Detects and repairs federation-level issues."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []
        self._actions: List[List[str]] = []
        self._cycles: int = 0

    def detect(self, civ) -> List[str]:
        self._cycles += 1
        issues: List[str] = []
        fed = getattr(civ, 'federation', None)
        prot = getattr(civ, 'protocol', None)
        bridge = getattr(civ, 'bridge_federation', None)
        sm = getattr(civ, 'state_machine_federation', None)

        if fed and not getattr(fed, 'members', []):
            issues.append("no_federation_members")
        if prot and not getattr(prot, '_exchange_history', []):
            issues.append("protocol_inactive")
        if bridge and not getattr(bridge, 'connections', []):
            issues.append("bridge_inactive")
        if sm and not getattr(sm, '_states', []):
            issues.append("state_machine_empty")

        self._logs.append({"ts": time.time(), "cycle": self._cycles, "detected": issues})
        return issues

    def heal(self, civ, issues: List[str]) -> List[str]:
        actions: List[str] = []
        sup = getattr(civ, 'super', None)
        snap = sup.unified_snapshot() if sup else {}

        for issue in issues:
            if issue == "no_federation_members" and hasattr(civ, 'federation'):
                civ.federation.add_member("civilization_v24_local")
                actions.append("added_default_member")
            if issue == "protocol_inactive" and hasattr(civ, 'protocol'):
                civ.protocol.exchange("civilization_v24_local", snap)
                actions.append("protocol_recovered")
            if issue == "bridge_inactive" and hasattr(civ, 'bridge_federation'):
                civ.bridge_federation.connect("civilization_v24_local")
                actions.append("bridge_recovered")
            if issue == "state_machine_empty" and hasattr(civ, 'state_machine_federation'):
                civ.state_machine_federation.add_state("recovered")
                actions.append("state_machine_recovered")

        self._actions.append(actions)
        self._logs.append({"ts": time.time(), "cycle": self._cycles, "actions": actions})
        return actions

    def snapshot(self) -> dict:
        return {"cycles": self._cycles, "logs": list(self._logs[-10:]), "actions": list(self._actions[-10:])}
