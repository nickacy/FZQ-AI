# src/fzq_ai/registry/agents.py
from __future__ import annotations

class AgentRegistry:
    def __init__(self):
        self._agents = {}

    def register(self, name: str, agent_cls):
        self._agents[name] = agent_cls

    def get(self, name: str):
        return self._agents.get(name)

    def all(self):
        return self._agents


# Global instance
global_registry = AgentRegistry()
