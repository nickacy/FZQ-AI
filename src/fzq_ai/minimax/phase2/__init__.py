"""src/fzq_ai/minimax/phase2/__init__.py

Minimax Phase 2 — Structural Feedback Layer (V24.3.4+).

Public API:
  - StructuralFeedback: Pydantic model for feedback report
  - MinimaxFeedbackEngine: generates feedback from strict_schema (+ optional original)
  - MinimaxFeedbackRouter: routes feedback to 6 downstream targets

Mandatory Rules (Phase 2):
  R1: Do NOT generate code
  R2: Do NOT modify business logic
  R3: Do NOT invent fields
  R4: Do NOT change structure definitions
  R5: ONLY generate structural feedback
  R6: Output MUST be JSON

V25+: optionally layer an LLM-backed "soft feedback" on top using the
System Prompt stored in `phase2/prompts/system_minimax_phase2.txt`.
"""
from __future__ import annotations

from .feedback_models import StructuralFeedback
from .feedback_engine import MinimaxFeedbackEngine
from .feedback_router import MinimaxFeedbackRouter

__all__ = [
    "StructuralFeedback",
    "MinimaxFeedbackEngine",
    "MinimaxFeedbackRouter",
]