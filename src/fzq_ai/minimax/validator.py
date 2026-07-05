"""src/fzq_ai/minimax/validator.py

Minimax — Strict Schema Validator (V24.3.1 reference implementation).

Public entry point: `StrictSchemaValidator.validate(raw) -> StrictSchema`.

Mandatory Rules enforced:
  R1: Do NOT fabricate or infer new facts (validator never invents strings)
  R2: Do NOT infer (only structural fixes; content preserved as-is)
  R3: MUST fill missing fields with empty arrays/objects
  R4: MUST repair types (str -> [str], dict -> [str], list of dicts -> list of str, etc.)
  R5: MUST maintain field name consistency (canonical field order)
  R6: Do NOT output natural language (output is always StrictSchema, not text)
"""
from __future__ import annotations
import json
import logging
from typing import Any, Dict, Union

from .schema import StrictSchema
from .repair import (
    SchemaRepairError,
    parse_json_text,
    repair_structure,
    repair_types,
    deep_validate,
)


logger = logging.getLogger(__name__)


class StrictSchemaValidator:
    """Validates and repairs DeepSeek Proto-Schema to FZQ-AI Strict Schema.

    Usage:
        validator = StrictSchemaValidator()
        result = validator.validate({"facts": ["x"], "actors": "y"})
        # result.facts == ["x"]
        # result.actors == ["y"]      # type repair
        # result.events == []          # field fill
        # result.risks.political == [] # nested fill
    """

    def __init__(self, *, strict: bool = True) -> None:
        """strict=True (default) raises on unparseable input; False returns empty schema."""
        self.strict = strict

    def validate(self, raw: Union[str, Dict[str, Any], None]) -> StrictSchema:
        """Validate + repair. Accepts dict, JSON string, or None.

        Returns StrictSchema. If `strict=False`, returns empty schema on parse failure.
        """
        # 1. Coerce input to dict
        parsed = self._coerce_to_dict(raw)
        if parsed is None:
            if self.strict:
                raise SchemaRepairError(
                    f"validate: cannot parse input of type {type(raw).__name__}"
                )
            logger.warning("minimax: parse failed, returning empty schema")
            return deep_validate({})

        # 2. R3: structural repair (fill missing fields)
        try:
            repaired = repair_structure(parsed)
        except SchemaRepairError as e:
            if self.strict:
                raise
            logger.warning(f"minimax: structural repair failed: {e}")
            return deep_validate({})

        # 3. R4: type repair (coerce single values, fix dict-as-list, etc.)
        repaired = repair_types(repaired)

        # 4. Final Pydantic validation (catches any remaining drift)
        return deep_validate(repaired)

    def _coerce_to_dict(self, raw: Union[str, Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        """Accept dict | JSON string | None -> dict | None."""
        if raw is None:
            return None
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            parsed = parse_json_text(raw)
            if isinstance(parsed, dict):
                return parsed
            return None
        return None

    # ============================================================
    # Civilization integration (V24.3.1 — optional, opt-in)
    # ============================================================

    def validate_with_civ(
        self,
        raw: Union[str, Dict[str, Any], None],
        civ: Any = None,
    ) -> StrictSchema:
        """Same as `validate` but writes repair metadata to civilization memory.

        civ=None: behaves identically to `validate`.
        civ=<CivilizationEngine>: best-effort remember('minimax_repaired_fields', ...)
        """
        result = self.validate(raw)

        if civ is not None and hasattr(civ, "remember"):
            try:
                repaired_fields = [
                    f for f in result.model_fields_set
                ]
                civ.remember("minimax_last_validated_at", str(_now()))
                civ.remember("minimax_last_repaired_fields", ",".join(repaired_fields) or "<none>")
                civ.remember("minimax_last_facts_count", str(len(result.facts)))
                civ.remember("minimax_last_risks_total", str(
                    len(result.risks.political)
                    + len(result.risks.economic)
                    + len(result.risks.social)
                    + len(result.risks.tech)
                    + len(result.risks.international)
                ))
            except Exception:
                # Civilization is best-effort; never break Minimax on civ failure
                pass

        return result


def _now() -> str:
    """ISO 8601 UTC timestamp (avoid importing datetime at module top level)."""
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat()