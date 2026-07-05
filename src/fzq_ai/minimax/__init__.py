"""src/fzq_ai/minimax/__init__.py

Minimax — Strict Schema Validator for FZQ-AI (V24.3.1+).

Public API:
  - StrictSchema: Pydantic model for FZQ-AI final structural baseline (13 fields)
  - StrictSchemaValidator: validates + repairs DeepSeek Proto-Schema to StrictSchema
  - SchemaRepairError: raised when input is unparseable / non-dict

Design choice (V24.3.1):
  Python validator (not LLM) — eliminates hallucination risk; guarantees R1-R6.

V25+: optionally layer an LLM-backed "soft validator" on top using the
System Prompt stored in `minimax/prompts/minimax_system.txt`.
"""
from __future__ import annotations

from .schema import (
    StrictSchema,
    StrictRisks,
    STRICT_SCHEMA_FIELD_ORDER,
)
from .validator import StrictSchemaValidator
from .repair import (
    SchemaRepairError,
    repair_structure,
    repair_types,
    parse_json_text,
)

__all__ = [
    "StrictSchema",
    "StrictRisks",
    "STRICT_SCHEMA_FIELD_ORDER",
    "StrictSchemaValidator",
    "SchemaRepairError",
    "repair_structure",
    "repair_types",
    "parse_json_text",
]