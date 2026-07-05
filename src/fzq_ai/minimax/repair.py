"""src/fzq_ai/minimax/repair.py

Schema repair primitives for Minimax.

Two repair operations, both idempotent and side-effect-free on well-formed input:
  - repair_structure: add missing top-level + nested fields with empty defaults
  - repair_types: coerce single values to lists, dict to list-of-strings, etc.

Implements R3 (fill missing fields) and R4 (repair types) from the Minimax
Mandatory Rules.
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Union

from .schema import (
    StrictSchema,
    StrictRisks,
    STRICT_SCHEMA_FIELD_ORDER,
    STRICT_RISKS_FIELD_ORDER,
)


class SchemaRepairError(ValueError):
    """Raised when input cannot be repaired (e.g. unparseable JSON, non-dict)."""
    pass


# JSON 3-tier parsing (mirrors ZhStructuredPipeline._parse_json) — re-used
# here so Minimax can accept either a dict or a raw LLM text blob.
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_JSON_BLOCK_RE = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)


def parse_json_text(text: str) -> Union[Dict[str, Any], List[Any], None]:
    """Best-effort JSON extraction. Returns None if no JSON found."""
    if not text:
        return None
    # 1. Direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # 2. Fenced code block
    m = _FENCE_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 3. First { ... } or [ ... ] block
    m = _JSON_BLOCK_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return None


def _ensure_list(value: Any) -> List[str]:
    """R4: coerce any value to List[str]."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, dict):
        # dict -> single string serialization (deterministic key order)
        try:
            return [json.dumps(value, ensure_ascii=False, sort_keys=True)]
        except Exception:
            return [str(value)]
    return [str(value)]


def _ensure_risks_dict(value: Any) -> Dict[str, List[str]]:
    """R4: coerce `risks` to dict with 5 sub-categories, all List[str]."""
    empty = {k: [] for k in STRICT_RISKS_FIELD_ORDER}

    if value is None:
        return empty
    if isinstance(value, list):
        # R4: risks is array -> convert to dict (best-effort: tag each entry by
        # content shape, not by intent; falls back to "political" bucket).
        for entry in value:
            if isinstance(entry, dict) and "category" in entry:
                cat = str(entry["category"]).lower()
                if cat in empty:
                    empty[cat].append(str(entry.get("text", "")))
                else:
                    empty["political"].append(str(entry.get("text", "")))
            elif isinstance(entry, str):
                empty["political"].append(entry)
        return empty
    if isinstance(value, dict):
        out = dict(empty)
        for k in STRICT_RISKS_FIELD_ORDER:
            if k in value:
                out[k] = _ensure_list(value[k])
        return out
    return empty


def repair_structure(raw: Dict[str, Any]) -> Dict[str, Any]:
    """R3: add missing top-level + nested fields with empty defaults.

    Returns a new dict (does not mutate input). Field order is canonical.
    """
    if not isinstance(raw, dict):
        raise SchemaRepairError(f"repair_structure: expected dict, got {type(raw).__name__}")

    # Top-level: enforce canonical order, fill missing with empty defaults
    repaired: Dict[str, Any] = {}
    for field in STRICT_SCHEMA_FIELD_ORDER:
        if field == "risks":
            repaired[field] = repair_structure_risks(raw.get(field))
        else:
            if field in raw and raw[field] is not None:
                repaired[field] = raw[field]
            else:
                repaired[field] = []
    return repaired


def repair_structure_risks(raw_risks: Any) -> Dict[str, List[str]]:
    """R3+R4 nested repair for the `risks` sub-object."""
    if raw_risks is None:
        return _ensure_risks_dict(None)
    return _ensure_risks_dict(raw_risks)


def repair_types(repaired: Dict[str, Any]) -> Dict[str, Any]:
    """R4: coerce top-level list-fields to List[str]; coerce `risks` to dict.

    Assumes input is already structurally complete (run repair_structure first).
    """
    for field in STRICT_SCHEMA_FIELD_ORDER:
        if field == "risks":
            repaired[field] = _ensure_risks_dict(repaired.get(field))
        else:
            repaired[field] = _ensure_list(repaired.get(field))
    return repaired


def deep_validate(repaired: Dict[str, Any]) -> StrictSchema:
    """Final Pydantic validation — raises ValidationError on any remaining drift."""
    return StrictSchema.model_validate(repaired)