# src/fzq_ai/llm/prompt_engine.py
# V24-Final — Unified Prompt Engine
"""
Centralised prompt builder for FZQ-AI.

All pipelines, agents, and orchestrators MUST use:
    prompt = PromptEngine.build(task_type="zh_risk_scan", intent="...", context={...})

Features:
  - Versioned templates (v24, future v25)
  - Falls back to "default" if task_type not found
  - Integrated with Router, Failover, Tracing, Monitoring
"""
from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.llm.prompt_templates_v24 import PROMPT_TEMPLATES


class PromptEngine:
    """Unified prompt builder with versioned templates."""

    def __init__(self, version: str = "v24"):
        self.version = version
        self._templates = PROMPT_TEMPLATES.get(version, PROMPT_TEMPLATES["v24"])

    @property
    def available_task_types(self) -> list:
        return list(self._templates.keys())

    def build(
        self,
        task_type: str,
        intent: str = "",
        context: Any = "",
    ) -> str:
        """Build a structured prompt from the template table.

        Args:
            task_type: e.g. zh_risk_scan, news, daily_report
            intent: what the user wants to accomplish
            context: supporting data or text

        Returns:
            formatted prompt string
        """
        template = self._templates.get(task_type, self._templates["default"])
        ctx_str = self._format_context(context)
        return template.format(intent=intent, context=ctx_str)

    def register_template(self, task_type: str, template: str) -> None:
        """Dynamically register a new template for a task type."""
        self._templates[task_type] = template

    @staticmethod
    def _format_context(context: Any) -> str:
        if isinstance(context, str):
            return context[:3000]
        if isinstance(context, dict):
            import json
            return json.dumps(context, ensure_ascii=False, default=str)[:3000]
        return str(context)[:3000]


# ── Global instance ──────────────────────────────────────────

prompt_engine = PromptEngine()


def build_prompt(task_type: str, intent: str = "", context: Any = "") -> str:
    """Convenience function: build a prompt using the default PromptEngine."""
    return prompt_engine.build(task_type, intent, context)
