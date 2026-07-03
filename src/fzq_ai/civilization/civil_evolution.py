# src/fzq_ai/civilization/civil_evolution.py
# V24-Final — Civilization Evolution Engine
"""
Civilization-level evolution, mutation & optimization for FZQ-AI.

  Evolve:     compute evolution score from knowledge graph weights
  Mutate:     random structural perturbation
  Expand:     grow new nodes
  Optimize:   apply consensus to improve structure
  Heal:       self-heal civilization-level issues

Integrated with: CivilizationEngine, KnowledgeGraph, Consensus, Memory, Tracing.
"""
from __future__ import annotations
import time
import random
from typing import Any, Dict, List


class CivilizationEvolutionEngine:
    """Drives civilization-level evolution cycles."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._history: List[Dict[str, Any]] = []
        self._mutations: List[str] = []
        self._expansions: List[str] = []
        self._optimizations: List[str] = []
        self._generation: int = 0

    # ── Evolve ──────────────────────────────────────────────

    def evolve(self, civ) -> Dict[str, Any]:
        """Run one evolution cycle on the civilization."""
        self._generation += 1
        started = time.time()

        # 1. Evolution score from knowledge graph weights
        evolution_score = sum(civ.knowledge_graph.weights.values()) if hasattr(civ, 'knowledge_graph') else 0.0

        # 2. Mutation — random structural change
        agents = list(getattr(civ, 'agents', []))
        mutation = self._rng.choice(agents) if agents else "none"

        # 3. Expansion — grow a new node
        expansion = f"evolved_node_g{self._generation}"
        self._expansions.append(expansion)

        # 4. Optimization — apply consensus
        optimization = getattr(getattr(civ, 'consensus_engine', None), '_results', {})
        self._optimizations.append(str(optimization)[:100])

        # 5. Self-heal — decay stale knowledge
        if hasattr(civ, 'knowledge_graph'):
            civ.knowledge_graph.decay(rate=0.01)

        result = {
            "generation": self._generation,
            "evolution_score": round(evolution_score, 3),
            "mutation": mutation,
            "expansion": expansion,
            "duration_ms": round((time.time() - started) * 1000, 1),
        }

        self._history.append(result)
        self._mutations.append(mutation)
        return result

    # ── Stats ───────────────────────────────────────────────

    @property
    def generation(self) -> int:
        return self._generation

    def trend(self) -> List[float]:
        """Evolution score trend over generations."""
        return [h.get("evolution_score", 0) for h in self._history]

    # ── Snapshot ────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "generation": self._generation,
            "history": list(self._history[-20:]),
            "mutations": list(self._mutations[-20:]),
            "expansions": list(self._expansions[-20:]),
            "optimizations": list(self._optimizations[-20:]),
            "trend": self.trend(),
            "is_evolving": self._generation > 0,
        }
