# src/fzq_ai/civilization/civil_federation_bridge.py
# V24-Final — Civilization Federation Bridge
"""
Bridge layer between federated civilizations.

  Connect:  establish persistent bridge links
  Exchange: snapshot & knowledge sharing over bridges
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationBridge:
    """Persistent bridge connections between civilizations."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []
        self._connections: List[str] = []
        self._snapshots: List[Dict[str, Any]] = []

    def connect(self, civ_name: str) -> Dict[str, Any]:
        if civ_name not in self._connections:
            self._connections.append(civ_name)
        entry = {"action": "connect", "civ": civ_name, "ts": time.time()}
        self._logs.append(entry)
        return entry

    def exchange(self, civ_name: str, civ_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"civ": civ_name, "ts": time.time(), "snapshot": civ_snapshot}
        self._snapshots.append(entry)
        self._logs.append({"action": "exchange", "civ": civ_name, "ts": time.time()})
        return entry

    @property
    def connections(self) -> List[str]:
        return list(self._connections)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "connections": list(self._connections),
            "active_bridges": len(self._connections),
            "exchanges": len(self._snapshots),
            "logs": list(self._logs[-10:]),
            "snapshots": list(self._snapshots[-5:]),
        }
