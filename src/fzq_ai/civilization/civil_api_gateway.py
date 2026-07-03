# src/fzq_ai/civilization/civil_api_gateway.py
# V24-Final — Civilization API Gateway
"""
Unified external API for the FZQ-AI civilization layer.

Exposes all civilization subsystems as structured endpoints.
Enables cross-system civilization cooperation (V25+).
"""
from __future__ import annotations
from typing import Any, Dict


class CivilizationAPIGateway:
    """Single entry point for all civilization queries."""

    def __init__(self, civ):
        self.civ = civ

    def get_structure(self) -> Dict[str, Any]:
        return self.civ.super.structure_tree() if hasattr(self.civ, 'super') else {}

    def get_snapshot(self) -> Dict[str, Any]:
        return self.civ.super.unified_snapshot() if hasattr(self.civ, 'super') else {}

    def get_consensus(self) -> Dict[str, Any]:
        return self._safe("consensus_engine")

    def get_parliament(self) -> Dict[str, Any]:
        return self._safe("parliament")

    def get_evolution(self) -> Dict[str, Any]:
        return self._safe("evolution")

    def get_meta(self) -> Dict[str, Any]:
        return self._safe("meta")

    def get_knowledge(self) -> Dict[str, Any]:
        return self._safe("knowledge_graph")

    def get_memory(self) -> Dict[str, Any]:
        return self._safe("memory")

    def get_all(self) -> Dict[str, Any]:
        return {
            "structure":   self.get_structure(),
            "snapshot":    self.get_snapshot(),
            "consensus":   self.get_consensus(),
            "parliament":  self.get_parliament(),
            "evolution":   self.get_evolution(),
            "meta":        self.get_meta(),
            "knowledge":   self.get_knowledge(),
            "memory":      self.get_memory(),
        }

    def _safe(self, attr: str) -> Any:
        obj = getattr(self.civ, attr, None)
        if obj and hasattr(obj, 'snapshot'):
            return obj.snapshot()
        return None
