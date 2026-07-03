# src/fzq_ai/civilization/civil_interconnect.py
# V24-Final — Civilization Interconnect Layer
"""
Cross-civilization network for FZQ-AI.

  Link:      establish peer connections with other civilizations
  Exchange:  bidirectional snapshot sharing
  Network:   inter-civilization topology (V25+ scale)
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationInterconnect:
    """Inter-civilization communication network."""

    def __init__(self):
        self._network: List[str] = []
        self._sync_logs: List[Dict[str, Any]] = []
        self._exchanges: List[Dict[str, Any]] = []

    def link(self, civ_name: str) -> bool:
        if civ_name not in self._network:
            self._network.append(civ_name)
        self._sync_logs.append({"action": "link", "civ": civ_name, "ts": time.time()})
        return True

    def exchange(self, civ_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"ts": time.time(), "snapshot": civ_snapshot}
        self._exchanges.append(entry)
        self._sync_logs.append({"action": "exchange", "ts": time.time()})
        return civ_snapshot

    @property
    def network(self) -> List[str]:
        return list(self._network)

    @property
    def peer_count(self) -> int:
        return len(self._network)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "network": list(self._network),
            "peer_count": self.peer_count,
            "exchanges": list(self._exchanges[-5:]),
            "sync_logs": list(self._sync_logs[-10:]),
        }
