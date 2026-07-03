# src/fzq_ai/utils/state_machine.py
# V24-Final — Agent State Machine
"""
Lifecycle state machine for FZQ-AI agents.

States: INIT → PLANNING → EXECUTING → REFLECTING → HEALING → COMPLETED

Drives: Pipeline execution, Orchestrator flow.
Integrated with: Planning, Goals, Reflection, Healing, Tracing, Monitoring.
"""
from __future__ import annotations
import time
from typing import Any, Dict, List

# ── States ───────────────────────────────────────────────────

STATE_INIT = "INIT"
STATE_PLANNING = "PLANNING"
STATE_EXECUTING = "EXECUTING"
STATE_REFLECTING = "REFLECTING"
STATE_HEALING = "HEALING"
STATE_COMPLETED = "COMPLETED"
STATE_ERROR = "ERROR"

ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    STATE_INIT:       [STATE_PLANNING, STATE_ERROR],
    STATE_PLANNING:   [STATE_EXECUTING, STATE_REFLECTING, STATE_ERROR],
    STATE_EXECUTING:  [STATE_REFLECTING, STATE_HEALING, STATE_COMPLETED, STATE_ERROR],
    STATE_REFLECTING: [STATE_HEALING, STATE_PLANNING, STATE_COMPLETED, STATE_ERROR],
    STATE_HEALING:    [STATE_PLANNING, STATE_EXECUTING, STATE_COMPLETED, STATE_ERROR],
    STATE_COMPLETED:  [STATE_INIT],  # restart
    STATE_ERROR:      [STATE_HEALING, STATE_INIT],
}

# ── State Machine ────────────────────────────────────────────

class StateMachine:
    """Per-agent lifecycle state machine."""

    def __init__(self, agent: str = ""):
        self.agent = agent
        self._current: str = STATE_INIT
        self._history: List[Dict[str, Any]] = []
        self._transition(STATE_INIT)

    # ── State management ────────────────────────────────────

    @property
    def current(self) -> str:
        return self._current

    @property
    def history(self) -> List[str]:
        return [h["state"] for h in self._history]

    @property
    def history_full(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def set(self, state: str) -> bool:
        """Transition to a new state. Returns True if allowed."""
        if state not in ALLOWED_TRANSITIONS.get(self._current, []):
            return False
        self._transition(state)
        return True

    def force(self, state: str) -> None:
        """Force transition (bypass validation)."""
        self._transition(state)

    def is_terminal(self) -> bool:
        return self._current in (STATE_COMPLETED, STATE_ERROR)

    # ── Internal ─────────────────────────────────────────────

    def _transition(self, state: str) -> None:
        entry = {
            "state": state,
            "timestamp": time.time(),
            "from": self._current,
        }
        self._current = state
        self._history.append(entry)
        if len(self._history) > 200:
            self._history = self._history[-100:]
        from fzq_ai.utils.logger import log_event
        log_event("state_machine.transition", agent=self.agent, state=state, previous=entry["from"])

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        return {
            "current": self._current,
            "history": self.history[-20:],
            "is_terminal": self.is_terminal(),
            "agent": self.agent,
        }


# ── Global registry ──────────────────────────────────────────

_state_machines: Dict[str, StateMachine] = {}


def get_state_machine(agent: str) -> StateMachine:
    """Get or create a state machine for an agent."""
    if agent not in _state_machines:
        _state_machines[agent] = StateMachine(agent)
    return _state_machines[agent]


def save_checkpoint(agent: str) -> dict:
    sm = _state_machines.get(agent)
    if not sm: return None
    import time
    return {'agent':agent,'current':sm.current,'history':list(sm.history),'ts':time.time()}

def restore_checkpoint(agent: str, cp: dict):
    sm = get_state_machine(agent)
    if cp and cp.get('current') in ALLOWED_TRANSITIONS:
        sm.force(cp['current'])
    return sm
