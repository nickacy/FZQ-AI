# src/fzq_ai/civilization/civilization_engine.py
# V24-Final — Civilization Layer Engine
"""
Top-level multi-agent civilization network for FZQ-AI.

  Civil graph:    agent → [linked agents] (hierarchy, roles, responsibilities)
  Civil memory:   shared knowledge across the civilization
  Civil goals:    civilization-level objectives
  Civil planning: cross-agent task decomposition
  Civil consensus: parliamentary decision-making via weighted voting

Integrated with: MultiAgentEngine, Orchestrator, Tracing, Monitoring.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional

from fzq_ai.utils.logger import log_event
from fzq_ai.utils.loop import run_agent_loop


class CivilizationEngine:
    """Top-level civilization network coordinator."""

    def __init__(self, name: str = "default"):
        self.name = name
        self._agents: Dict[str, Dict[str, Any]] = {}      # name → {role, priority}
        self._graph: Dict[str, List[str]] = {}             # name → [linked agents]
        self._civil_memory: Dict[str, Any] = {}            # shared knowledge
        self._civil_goals: Dict[str, Any] = {}             # civilization objectives
        self._results: List[Dict[str, Any]] = []
        self._consensus_log: List[Dict[str, Any]] = []

    # ── Agent management ────────────────────────────────────

    def add_agent(self, name: str, role: str = "citizen", priority: int = 1) -> None:
        self._agents[name] = {"role": role, "priority": priority}
        self._graph.setdefault(name, [])

    def link(self, source: str, target: str) -> None:
        """Create a directed link between two agents."""
        if source in self._graph:
            if target not in self._graph[source]:
                self._graph[source].append(target)

    @property
    def agents(self) -> List[str]:
        return list(self._agents.keys())

    @property
    def graph(self) -> Dict[str, List[str]]:
        return dict(self._graph)

    # ── Civilization memory ──────────────────────────────────

    def remember(self, key: str, value: Any) -> None:
        self._civil_memory[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._civil_memory.get(key, default)

    # ── Execution ────────────────────────────────────────────

    def run(self, intent: str) -> Dict[str, Any]:
        """Execute a civilization-level task across all agents."""
        started = time.time()
        self._results = []

        # Run agents in priority order
        ordered = sorted(self._agents.items(), key=lambda x: -x[1].get("priority", 1))
        for name, meta in ordered:
            result = self._run_agent(name, intent, meta)
            self._results.append(result)

        # Generate consensus
        consensus = self._generate_consensus()

        log_event("civilization.run_complete",
            civ=self.name, agents=len(self._agents),
            duration_ms=(time.time() - started) * 1000)

        return {
            "graph": self.graph,
            "results": self._results,
            "consensus": consensus,
            "civil_memory_snapshot": dict(self._civil_memory),
        }

    def _run_agent(self, name: str, intent: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        try:
            cycle = run_agent_loop(name, intent)
        except Exception as e:
            cycle = {"error": str(e), "trace": ["error"]}
        return {
            "agent": name,
            "role": meta.get("role", "citizen"),
            "output": cycle.get("output"),
            "reflection": cycle.get("reflection"),
            "state_machine": cycle.get("state_machine", {}),
            "duration_ms": round((time.time() - t0) * 1000, 1),
        }

    # ── Consensus ────────────────────────────────────────────

    def _generate_consensus(self) -> Dict[str, Any]:
        """Generate parliamentary consensus from agent outputs."""
        votes = {}
        for r in self._results:
            if r.get("output"):
                key = r["output"][:50]
                votes[key] = votes.get(key, 0) + self._agents.get(r["agent"], {}).get("priority", 1)
        winner = max(votes, key=votes.get) if votes else None
        entry = {
            "timestamp": time.time(), "votes": votes, "consensus": winner,
            "participants": len(self._results),
        }
        self._consensus_log.append(entry)
        return entry

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "agents": self.agents,
            "graph": self.graph,
            "roles": {n: m["role"] for n, m in self._agents.items()},
            "results": list(self._results),
            "civil_memory_keys": list(self._civil_memory.keys()),
        }


# ── Global instance ──────────────────────────────────────────

global_civilization = CivilizationEngine("fzq-civ")
