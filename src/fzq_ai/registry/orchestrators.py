# src/fzq_ai/registry/orchestrators.py
from __future__ import annotations

class OrchestratorRegistry:
    def __init__(self):
        self._orchestrators = {}

    def register(self, name: str, orchestrator_cls):
        self._orchestrators[name] = orchestrator_cls

    def get(self, name: str):
        return self._orchestrators.get(name)

    def all(self):
        return self._orchestrators


global_registry = OrchestratorRegistry()
