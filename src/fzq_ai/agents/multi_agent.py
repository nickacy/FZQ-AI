# src/fzq_ai/agents/multi_agent.py
# V24-Final — Multi-Agent Collaboration Engine
"""
Multi-agent coordination for FZQ-AI.

Features:
  - Parallel agent execution
  - Shared memory (opt-in)
  - Collaboration chain recording
  - Inter-agent reflection

Integrated with: Orchestrator, Loop, StateMachine, Tracing, Monitoring.
"""
from __future__ import annotations
import logging
import time
from typing import Any, Dict, List, Optional

from fzq_ai.utils.logger import log_event
from fzq_ai.utils.memory import global_memory
from fzq_ai.utils.loop import run_agent_loop
_logger = logging.getLogger("fzq_ai.multi_agent")


class MultiAgentEngine:
    """Coordinates multiple agents for a shared task.

    V24-R2: accepts an optional `civilization` handle. When provided, each
    per-agent run writes a `multi_agent.<agent>` memory key, and the engine
    remembers the final collaboration chain.
    """

    def __init__(self):
        self._agents: List[str] = []
        self._results: List[Dict[str, Any]] = []
        self._collaboration_chain: List[str] = []

    # ── Agent management ────────────────────────────────────

    def add(self, agent_name: str) -> None:
        self._agents.append(agent_name)

    def remove(self, agent_name: str) -> None:
        if agent_name in self._agents:
            self._agents.remove(agent_name)

    @property
    def agents(self) -> List[str]:
        return list(self._agents)

    @property
    def collaboration_chain(self) -> List[str]:
        return list(self._collaboration_chain)

    # ── Execution ────────────────────────────────────────────

    def run(self, intent: str, shared_memory: bool = False, civilization: Any = None) -> List[Dict[str, Any]]:
        """Execute task across all agents. Returns per-agent results.

        V24-R2: `civilization` is optional; when provided, per-agent outputs
        are mirrored to civilization memory and the chain is recorded.
        """
        self._results = []
        self._collaboration_chain = []
        started = time.time()

        for agent_name in self._agents:
            agent_result = self._run_one(agent_name, intent, shared_memory, civilization)
            self._results.append(agent_result)
            self._collaboration_chain.append(agent_name)

        log_event("multi_agent.run_complete",
            agents=self._agents, duration_ms=(time.time() - started) * 1000,
            chain=self._collaboration_chain)

        # V24-R2: post-run civilization snapshot
        if civilization and hasattr(civilization, "remember"):
            try:
                civilization.remember("multi_agent_last_chain", list(self._collaboration_chain))
                civilization.remember("multi_agent_last_count", len(self._results))
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        return self._results

    def _run_one(self, agent_name: str, intent: str, shared: bool, civilization: Any = None) -> Dict[str, Any]:
        t0 = time.time()
        try:
            cycle = run_agent_loop(agent_name, intent)
            if shared:
                # Share output with other agents via memory
                global_memory.remember(
                    f"shared_{agent_name}", "last_output", cycle.get("output"))
            # V24-R2: mirror per-agent output to civilization (best-effort)
            if civilization and hasattr(civilization, "remember"):
                try:
                    civilization.remember(
                        f"multi_agent.{agent_name}", "last_output", cycle.get("output"))
                except Exception:
                    _logger.warning("Suppressed error", exc_info=True)
        except Exception as e:
            cycle = {"error": str(e), "trace": ["error"]}

        return {
            "agent": agent_name,
            "output": cycle.get("output"),
            "reflection": cycle.get("reflection"),
            "healing": cycle.get("healing"),
            "trace": cycle.get("trace", []),
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "state_machine": cycle.get("state_machine", {}),
        }

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agents": self.agents,
            "results": list(self._results),
            "collaboration_chain": self.collaboration_chain,
            "total_agents": len(self._agents),
        }


# ── Global instance ──────────────────────────────────────────

global_multi_agent = MultiAgentEngine()
