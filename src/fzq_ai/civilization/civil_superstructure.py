# src/fzq_ai/civilization/civil_superstructure.py
# V24-Final — Civilization Superstructure
"""
Top-level abstraction over the entire civilization layer.

  Structure Tree:   hierarchical overview of all civil modules
  Unified Snapshot: single call to snapshot the entire civilization
  Metadata:         version, agent count, graph density
  API:              unified entry point for external consumers

This is the "API surface" of the FZQ-AI civilization layer.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationSuperstructure:
    """Unified top-level view of the civilization."""

    def __init__(self, civ):
        self.civ = civ
        self._created_at = time.time()
        self._version = "v24"

    # ── Structure tree ──────────────────────────────────────

    def structure_tree(self) -> Dict[str, Any]:
        """Hierarchical overview of all civilization modules."""
        kg = getattr(self.civ, 'knowledge_graph', None)
        return {
            "memory":             list(self._safe_snapshot("memory").keys()) if hasattr(self.civ, 'memory') else [],
            "knowledge_graph":    {
                "nodes": kg.node_count() if kg else 0,
                "edges": kg.edge_count() if kg else 0,
            } if kg else {},
            "consensus":          list(self._safe_snapshot("consensus_engine").keys()) if hasattr(self.civ, 'consensus_engine') else [],
            "parliament":         list(self._safe_snapshot("parliament").keys()) if hasattr(self.civ, 'parliament') else [],
            "evolution":          list(self._safe_snapshot("evolution").keys()) if hasattr(self.civ, 'evolution') else [],
            "meta_controller":    list(self._safe_snapshot("meta").keys()) if hasattr(self.civ, 'meta') else [],
        }

    # ── Unified snapshot ────────────────────────────────────

    def unified_snapshot(self) -> Dict[str, Any]:
        """Single call to snapshot entire civilization."""
        agents = getattr(self.civ, 'agents', [])
        graph = getattr(self.civ, 'graph', {})
        return {
            "version": self._version,
            "timestamp": time.time(),
            "uptime": round(time.time() - self._created_at, 1),
            "structure_tree": self.structure_tree(),
            "agents": list(agents) if isinstance(agents, dict) else agents,
            "graph": graph,
            "memory":            self._safe_snapshot("memory"),
            "knowledge_graph":   self._safe_snapshot("knowledge_graph"),
            "consensus":         self._safe_snapshot("consensus_engine"),
            "parliament":        self._safe_snapshot("parliament"),
            "evolution":         self._safe_snapshot("evolution"),
            "meta_controller":   self._safe_snapshot("meta"),
        }

    # ── Metadata ────────────────────────────────────────────

    def metadata(self) -> Dict[str, Any]:
        kg = getattr(self.civ, 'knowledge_graph', None)
        return {
            "version": self._version,
            "agent_count": len(getattr(self.civ, 'agents', [])),
            "graph_density": sum(len(v) for v in getattr(self.civ, 'graph', {}).values()) if hasattr(self.civ, 'graph') else 0,
            "knowledge_nodes": kg.node_count() if kg else 0,
            "knowledge_edges": kg.edge_count() if kg else 0,
            "uptime": round(time.time() - self._created_at, 1),
        }

    # ── Helpers ─────────────────────────────────────────────

    def _safe_snapshot(self, attr: str) -> Any:
        obj = getattr(self.civ, attr, None)
        if obj and hasattr(obj, 'snapshot'):
            return obj.snapshot()
        return None
