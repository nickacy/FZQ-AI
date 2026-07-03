# src/fzq_ai/civilization/civil_knowledge_graph.py
# V24-Final — Civilization Knowledge Graph
"""
Civilization-level structured knowledge graph for FZQ-AI.

  Nodes:     knowledge entries with values
  Edges:     relationships between knowledge nodes
  Weights:   importance scores (auto-propagated)
  Evolution: weight propagation + decay
  Snapshot:  full graph export

Integrated with: CivilizationEngine, CivilMemory, Orchestrator, Tracing.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationKnowledgeGraph:
    """Structured knowledge graph for the civilization layer."""

    def __init__(self):
        self.nodes: Dict[str, Any] = {}       # key → value
        self.edges: Dict[str, List[str]] = {} # key → [related keys]
        self.weights: Dict[str, float] = {}   # key → importance (0–10)
        self._history: List[Dict[str, Any]] = []

    # ── Node management ─────────────────────────────────────

    def add_node(self, key: str, value: Any, weight: float = 1.0) -> None:
        self.nodes[key] = value
        self.edges.setdefault(key, [])
        self.weights[key] = min(10.0, max(0.0, weight))
        self._log("node_added", key=key)

    def has_node(self, key: str) -> bool:
        return key in self.nodes

    # ── Edge management ─────────────────────────────────────

    def add_edge(self, source: str, target: str, bidirectional: bool = False) -> None:
        """Create a relationship between two knowledge nodes."""
        self.edges.setdefault(source, [])
        if target not in self.edges[source]:
            self.edges[source].append(target)
        if bidirectional:
            self.edges.setdefault(target, [])
            if source not in self.edges[target]:
                self.edges[target].append(source)
        self._log("edge_added", source=source, target=target)

    # ── Weight propagation ──────────────────────────────────

    def propagate(self, key: str, factor: float = 0.1) -> None:
        """Propagate importance to neighbors."""
        for neighbor in self.edges.get(key, []):
            if neighbor in self.weights:
                self.weights[neighbor] = min(10.0, self.weights[neighbor] + factor)
        self._log("propagated", key=key)

    def decay(self, rate: float = 0.01) -> None:
        """Apply global weight decay."""
        for k in self.weights:
            self.weights[k] = max(0.0, self.weights[k] - rate)

    # ── Query ───────────────────────────────────────────────

    def top_nodes(self, n: int = 5) -> List[str]:
        """Return highest-weighted nodes."""
        return sorted(self.weights, key=lambda k: self.weights[k], reverse=True)[:n]

    def neighbors(self, key: str) -> List[str]:
        return list(self.edges.get(key, []))

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return sum(len(v) for v in self.edges.values())

    # ── Snapshot ────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "nodes": dict(self.nodes),
            "edges": {k: list(v) for k, v in self.edges.items()},
            "weights": dict(self.weights),
            "top_nodes": self.top_nodes(5),
            "node_count": self.node_count(),
            "edge_count": self.edge_count(),
        }

    # ── Logging ─────────────────────────────────────────────

    def _log(self, action: str, **meta: Any) -> None:
        self._history.append({"ts": time.time(), "action": action, **meta})
        if len(self._history) > 200:
            self._history = self._history[-100:]
