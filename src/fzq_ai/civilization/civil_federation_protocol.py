# src/fzq_ai/civilization/civil_federation_protocol.py
# V24-Final — Civilization Federation Protocol
"""
Cross-civilization communication protocol layer.

  Exchange:  snapshot sharing between civilizations
  Sync:      state synchronization
  Protocol:  standardized inter-civ message format (V25+ JSON schema)
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationProtocol:
    """Standardized protocol for federation communication."""

    def __init__(self, version: str = "v24"):
        self._version = version
        self._logs: List[Dict[str, Any]] = []
        self._exchange_history: List[Dict[str, Any]] = []
        self._sync_history: List[Dict[str, Any]] = []

    def exchange(self, civ_name: str, civ_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"civ": civ_name, "ts": time.time(), "snapshot": civ_snapshot}
        self._exchange_history.append(entry)
        self._logs.append({"action": "exchange", "civ": civ_name, "ts": time.time()})
        return entry

    def sync(self, civ_name: str, civ_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"civ": civ_name, "ts": time.time(), "snapshot": civ_snapshot}
        self._sync_history.append(entry)
        self._logs.append({"action": "sync", "civ": civ_name, "ts": time.time()})
        return entry

    def snapshot(self) -> Dict[str, Any]:
        return {
            "version": self._version,
            "logs": list(self._logs[-10:]),
            "exchange_history": list(self._exchange_history[-5:]),
            "sync_history": list(self._sync_history[-5:]),
            "total_exchanges": len(self._exchange_history),
            "total_syncs": len(self._sync_history),
        }
