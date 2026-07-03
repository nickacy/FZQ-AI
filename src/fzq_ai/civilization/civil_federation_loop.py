# src/fzq_ai/civilization/civil_federation_loop.py
# V24-Final — Civilization Federation Loop
"""Federation lifecycle loop — coordinates all federation modules."""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationLoop:
    """Orchestrates federation cycles."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []
        self._results: List[Dict[str, Any]] = []
        self._cycles: int = 0

    def run(self, civ) -> Dict[str, Any]:
        self._cycles += 1
        result = {
            "cycle": self._cycles,
            "ts": time.time(),
            "federation": self._snapshot(civ, "federation"),
            "council": self._snapshot(civ, "council"),
            "intelligence": self._snapshot(civ, "intelligence"),
            "protocol": self._snapshot(civ, "protocol"),
            "bridge": self._snapshot(civ, "bridge_federation"),
            "state_machine": self._snapshot(civ, "state_machine_federation"),
        }
        self._results.append(result)
        self._logs.append({"action": "loop", "cycle": self._cycles, "ts": time.time()})
        return result

    def _snapshot(self, civ, attr: str) -> Any:
        obj = getattr(civ, attr, None)
        return obj.snapshot() if obj and hasattr(obj, 'snapshot') else None

    def snapshot(self) -> dict:
        return {"cycles": self._cycles, "logs": list(self._logs[-10:]), "results": list(self._results[-5:])}
