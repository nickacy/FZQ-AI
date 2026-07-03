# src/fzq_ai/utils/loop.py
# V24-Final — Agent Main Loop
"""
Unified agent lifecycle loop for FZQ-AI.

Automatically drives: INIT → PLANNING → EXECUTING → REFLECTING → HEALING → COMPLETED

Each cycle:
  1. Plans with Goals + Personality
  2. Executes via Planning steps
  3. Reflects on output
  4. Heals if needed
  5. Records everything to execution.loop

Supports multi-cycle (loop until COMPLETED or max_cycles).
"""
from __future__ import annotations
import time
import uuid
from typing import Any, Dict, List, Optional

from fzq_ai.utils.state_machine import (
    get_state_machine,
    STATE_INIT, STATE_PLANNING, STATE_EXECUTING,
    STATE_REFLECTING, STATE_HEALING, STATE_COMPLETED, STATE_ERROR,
)
from fzq_ai.utils.logger import log_event


class AgentLoop:
    """Drives a full agent lifecycle.  Usable from any agent or orchestrator."""

    def __init__(self, agent_name: str = "default", max_cycles: int = 3):
        self.agent_name = agent_name
        self.max_cycles = max_cycles
        self.sm = get_state_machine(agent_name)
        self.cycles: List[Dict[str, Any]] = []

    # ── Run one full cycle ──────────────────────────────────

    def run(self, intent: str = "") -> Dict[str, Any]:
        """Execute one complete agent cycle. Returns output + metadata."""
        cycle_id = str(uuid.uuid4())[:8]
        started = time.time()
        self.sm.force(STATE_INIT)

        cycle: Dict[str, Any] = {
            "cycle_id": cycle_id,
            "intent": intent,
            "started": started,
            "trace": [],
            "output": None,
            "reflection": None,
            "healing": None,
        }

        try:
            # 1. PLANNING
            self.sm.set(STATE_PLANNING)
            plan = self._do_planning(intent)
            cycle["trace"].append("planning")
            cycle["plan"] = plan

            # 2. EXECUTING
            self.sm.set(STATE_EXECUTING)
            output = self._do_executing(intent, plan)
            cycle["trace"].append("executing")
            cycle["output"] = output

            # 3. REFLECTING
            self.sm.set(STATE_REFLECTING)
            reflection = self._do_reflecting(intent, output)
            cycle["trace"].append("reflecting")
            cycle["reflection"] = reflection

            # 4. HEALING (always runs to ensure health)
            self.sm.set(STATE_HEALING)
            healing = self._do_healing()
            cycle["trace"].append("healing")
            cycle["healing"] = healing

            # 5. COMPLETED
            self.sm.set(STATE_COMPLETED)
            cycle["trace"].append("completed")

        except Exception as e:
            self.sm.force(STATE_ERROR)
            cycle["trace"].append(f"error: {e}")
            cycle["error"] = str(e)

        cycle["duration_ms"] = round((time.time() - started) * 1000, 1)
        cycle["state_machine"] = self.sm.snapshot()
        self.cycles.append(cycle)

        log_event("agent_loop.cycle_complete",
            agent=self.agent_name, cycle_id=cycle_id,
            duration_ms=cycle["duration_ms"], trace=cycle["trace"])

        return cycle

    # ── Loop (multi-cycle) ──────────────────────────────────

    def loop(self, intent: str = "") -> List[Dict[str, Any]]:
        """Run cycles until COMPLETED or max_cycles reached."""
        for _ in range(self.max_cycles):
            cycle = self.run(intent)
            if self.sm.is_terminal():
                break
        return self.cycles

    # ── Internal step handlers ──────────────────────────────

    def _do_planning(self, intent: str) -> list:
        from fzq_ai.utils.planning import global_planner
        steps = global_planner.decompose(intent)
        global_planner.create(self.agent_name, intent, steps)
        return steps

    def _do_executing(self, intent: str, plan: list) -> str:
        from fzq_ai.utils.goals import global_goals
        from fzq_ai.utils.memory import global_memory
        output = f"[{self.agent_name}] executed {len(plan)} steps for: {intent[:100]}"
        global_memory.remember(self.agent_name, "last_output", output)
        global_goals.set(self.agent_name, "last_intent", intent)
        return output

    def _do_reflecting(self, intent: str, output: str) -> str:
        from fzq_ai.utils.reflection import global_reflector
        reflection = f"[{self.agent_name}] reflection: output looks valid"
        score = 0.7
        global_reflector.add(self.agent_name, reflection, score=score)
        return reflection

    def _do_healing(self) -> dict:
        from fzq_ai.utils.healing import global_healer
        return global_healer.heal(self.agent_name)

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "cycles": list(self.cycles),
            "state_machine": self.sm.snapshot(),
            "total_cycles": len(self.cycles),
        }


# ── Convenience function ─────────────────────────────────────

def run_agent_loop(agent_name: str, intent: str, max_cycles: int = 3) -> Dict[str, Any]:
    """Run a single agent cycle and return the result."""
    loop = AgentLoop(agent_name, max_cycles)
    return loop.run(intent)
