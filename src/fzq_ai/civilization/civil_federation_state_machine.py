# src/fzq_ai/civilization/civil_federation_state_machine.py
# V24-Final — Civilization Federation State Machine
"""
Lifecycle state machine for the civilization federation.

  States:       federation lifecycle phases
  Transitions:  state changes with reasons
"""
from __future__ import annotations
import time
from typing import Any, Dict, List


class CivilizationFederationStateMachine:
    """Federation-level state tracking."""

    def __init__(self):
        self._states: List[str] = []
        self._transitions: List[Dict[str, Any]] = []
        self._current: str = "init"

    def add_state(self, state: str) -> None:
        self._states.append(state)
        self._current = state

    def transition(self, from_state: str, to_state: str, reason: str = "") -> Dict[str, Any]:
        entry = {"from": from_state, "to": to_state, "reason": reason, "ts": time.time()}
        self._transitions.append(entry)
        self._current = to_state
        if to_state not in self._states:
            self._states.append(to_state)
        return entry

    @property
    def current(self) -> str:
        return self._current

    def snapshot(self) -> Dict[str, Any]:
        return {
            "current": self._current,
            "states": list(self._states),
            "transitions": list(self._transitions[-20:]),
            "total_transitions": len(self._transitions),
        }
