# src/fzq_ai/civilization/civil_federation_orchestrator.py
# V24-Final — Civilization Federation Orchestrator
"""
Top-level federation orchestrator — coordinates all federation modules.

  Orchestrate:  run one full federation cycle across all subsystems
  Snapshot:     unified view of federation state
  Logs:         execution audit trail
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationOrchestrator:
    """Coordinates all federation subsystems in a single cycle."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []
        self._snapshots: List[Dict[str, Any]] = []
        self._cycles: int = 0

    def orchestrate(self, civ) -> Dict[str, Any]:
        """Run one full federation orchestration cycle."""
        self._cycles += 1
        started = time.time()

        result = {
            "cycle": self._cycles,
            "ts": started,
            "federation":       self._snap(civ, "federation"),
            "council":          self._snap(civ, "council"),
            "intelligence":     self._snap(civ, "intelligence"),
            "protocol":         self._snap(civ, "protocol"),
            "bridge":           self._snap(civ, "bridge_federation"),
            "state_machine":    self._snap(civ, "state_machine_federation"),
            "loop":             self._snap(civ, "loop_federation"),
            "duration_ms":      round((time.time() - started) * 1000, 1),
        }

        self._snapshots.append(result)
        self._logs.append({"action": "orchestrate", "cycle": self._cycles, "ts": started})

        if hasattr(civ, 'memory'):
            civ.memory.record_event("Federation orchestrator cycle completed", cycle=self._cycles)

        return result

    def _snap(self, civ, attr: str) -> Any:
        obj = getattr(civ, attr, None)
        return obj.snapshot() if obj and hasattr(obj, 'snapshot') else None

    def snapshot(self) -> Dict[str, Any]:
        return {
            "cycles": self._cycles,
            "logs": list(self._logs[-10:]),
            "snapshots": list(self._snapshots[-5:]),
        }
