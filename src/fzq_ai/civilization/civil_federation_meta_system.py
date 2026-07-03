# src/fzq_ai/civilization/civil_federation_meta_system.py
# V24-Final — Civilization Federation MetaSystem
"""Meta-system that analyzes & governs all federation subsystems."""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationMetaSystem:
    """Top-level governance over the entire federation."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []
        self._snapshots: List[Dict[str, Any]] = []
        self._cycles: int = 0

    def analyze(self, civ) -> Dict[str, Any]:
        self._cycles += 1
        snapshot = {
            "cycle": self._cycles,
            "ts": time.time(),
            "federation":    self._snap(civ, "federation"),
            "council":       self._snap(civ, "council"),
            "intelligence":  self._snap(civ, "intelligence"),
            "protocol":      self._snap(civ, "protocol"),
            "bridge":        self._snap(civ, "bridge_federation"),
            "state_machine": self._snap(civ, "state_machine_federation"),
            "loop":          self._snap(civ, "loop_federation"),
            "orchestrator":  self._snap(civ, "orchestrator_federation"),
        }
        self._snapshots.append(snapshot)
        self._logs.append({"action": "analyze", "cycle": self._cycles, "ts": time.time()})
        return snapshot

    def _snap(self, civ, attr: str) -> Any:
        obj = getattr(civ, attr, None)
        return obj.snapshot() if obj and hasattr(obj, 'snapshot') else None

    def snapshot(self) -> dict:
        return {"cycles": self._cycles, "logs": list(self._logs[-10:]), "snapshots": list(self._snapshots[-5:])}
