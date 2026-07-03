# src/fzq_ai/civilization/civil_external_bridge.py
# V24-Final — Civilization External Bridge
"""
External connectivity layer for FZQ-AI civilization.

  Connect:  establish links to external systems
  Sync:     synchronize civilization state with externals
  Bridge:   cross-civilization communication channel (V25+)
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationExternalBridge:
    """Bridge between FZQ-AI civilization and external systems."""

    def __init__(self):
        self._connections: List[str] = []
        self._external_states: List[Dict[str, Any]] = []
        self._bridge_logs: List[Dict[str, Any]] = []
        self._sync_count: int = 0

    def connect(self, target: str, meta: Dict[str, Any] = None) -> bool:
        if target not in self._connections:
            self._connections.append(target)
        self._bridge_logs.append({
            "action": "connect", "target": target, "ts": time.time(), "meta": meta or {},
        })
        return True

    def sync(self, civ_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        self._sync_count += 1
        entry = {"ts": time.time(), "count": self._sync_count, "snapshot": civ_snapshot}
        self._external_states.append(entry)
        self._bridge_logs.append({"action": "sync", "ts": time.time(), "count": self._sync_count})
        return civ_snapshot

    @property
    def connections(self) -> List[str]:
        return list(self._connections)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "connections": list(self._connections),
            "external_states": list(self._external_states[-5:]),
            "bridge_logs": list(self._bridge_logs[-10:]),
            "sync_count": self._sync_count,
            "active_connections": len(self._connections),
        }
