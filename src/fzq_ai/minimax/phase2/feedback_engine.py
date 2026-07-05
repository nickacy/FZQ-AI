"""src/fzq_ai/minimax/phase2/feedback_engine.py

MinimaxFeedbackEngine — Phase 2 core logic.

Generates `StructuralFeedback` from a Phase-1 repaired StrictSchema,
optionally diffed against the original input to surface missing/type/risk/order repairs.

Mandatory Rules:
  R1: Do NOT generate code (suggestions are structural prose only)
  R2: Do NOT modify business logic (engine is pure read-only)
  R3: Do NOT invent fields (all reported fields come from canonical schema)
  R4: Do NOT change structure definitions (strict_schema is treated as immutable)
  R5: ONLY generate structural feedback
  R6: Output MUST be JSON (StructuralFeedback.model_dump() is JSON-safe)
"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Dict, List, Optional

from ..schema import (
    STRICT_SCHEMA_FIELD_ORDER,
    STRICT_RISKS_FIELD_ORDER,
)
from .feedback_models import StructuralFeedback


logger = logging.getLogger(__name__)


# Mapping of canonical types per field — used to detect type repairs
_CANONICAL_TYPES = {
    # top-level fields all expect List[str]
    **{f: list for f in STRICT_SCHEMA_FIELD_ORDER if f != "risks"},
    "risks": dict,
}


class MinimaxFeedbackEngine:
    """Generate structural feedback from Phase 1 output.

    Usage:
        engine = MinimaxFeedbackEngine()
        feedback = engine.generate(
            strict_schema={"facts": ["x"], "events": [], ...},
            original_input={"facts": ["x"]},  # optional
        )
        # feedback.missing_fields == ["events", "actors", ...]
        # feedback.consistency_score == ~12.5  (1/8 fields populated)
    """

    def __init__(self) -> None:
        self.source = "minimax_phase2"

    def generate(
        self,
        strict_schema: Dict[str, Any],
        original_input: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> StructuralFeedback:
        """Build a StructuralFeedback report.

        Args:
            strict_schema: Phase-1 repaired StrictSchema dump (StrictSchema.model_dump())
            original_input: Pre-repair input dict, used to compute missing/type/risk/order reports
            trace_id: Parent pipeline trace_id (for correlation)

        Returns:
            StructuralFeedback (Pydantic model, JSON-serializable per R6)
        """
        if not isinstance(strict_schema, dict):
            raise TypeError(f"strict_schema must be dict, got {type(strict_schema).__name__}")

        # R3+R4: read-only — never mutate strict_schema or original_input
        missing = self._find_missing(strict_schema, original_input)
        type_repairs = self._find_type_repairs(strict_schema, original_input)
        risk_repairs = self._find_risk_repairs(strict_schema, original_input)
        order_repairs = self._find_order_repairs(strict_schema, original_input)

        consistency = self._consistency_score(strict_schema)
        risk = self._risk_score(strict_schema)

        suggestions = self._suggest(
            strict_schema=strict_schema,
            missing=missing,
            type_repairs=type_repairs,
            risk_repairs=risk_repairs,
            consistency=consistency,
            risk=risk,
        )

        return StructuralFeedback(
            source=self.source,
            missing_fields=missing,
            type_repairs=type_repairs,
            risk_repairs=risk_repairs,
            order_repairs=order_repairs,
            consistency_score=consistency,
            risk_score=risk,
            suggestions=suggestions,
            trace_id=trace_id or str(uuid.uuid4()),
        )

    # ============================================================
    # Detection methods — read-only, return lists of strings
    # ============================================================

    def _find_missing(
        self, strict_schema: Dict[str, Any], original_input: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Report fields that were absent from original input (Phase 1 filled them)."""
        if original_input is None:
            return []
        missing: List[str] = []
        for field in STRICT_SCHEMA_FIELD_ORDER:
            if field == "risks":
                # nested check
                original_risks = original_input.get("risks") or {}
                if not isinstance(original_risks, dict):
                    missing.append("risks")
                    continue
                for sub in STRICT_RISKS_FIELD_ORDER:
                    if sub not in original_risks:
                        missing.append(f"risks.{sub}")
                continue
            if field not in original_input:
                missing.append(field)
        return missing

    def _find_type_repairs(
        self, strict_schema: Dict[str, Any], original_input: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Report fields where original input had wrong type (Phase 1 coerced)."""
        if original_input is None:
            return []
        repairs: List[str] = []
        for field, expected_type in _CANONICAL_TYPES.items():
            original_value = original_input.get(field)
            if original_value is None:
                continue
            if field == "risks":
                # Special handling: risks must be dict, original may be list
                if not isinstance(original_value, dict):
                    repairs.append(f"risks (was {type(original_value).__name__}, expected dict)")
                continue
            if not isinstance(original_value, expected_type):
                repairs.append(
                    f"{field} (was {type(original_value).__name__}, expected {expected_type.__name__})"
                )
        return repairs

    def _find_risk_repairs(
        self, strict_schema: Dict[str, Any], original_input: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Report risk sub-categories that required structural repair."""
        if original_input is None:
            return []
        repairs: List[str] = []
        original_risks = original_input.get("risks")
        if original_risks is None:
            return []
        # Case 1: risks is a list (Phase 1 converts to dict)
        if isinstance(original_risks, list):
            repairs.append(
                f"risks (was list[{len(original_risks)}], converted to 5-category dict)"
            )
            return repairs
        # Case 2: risks is a dict but missing sub-categories
        if isinstance(original_risks, dict):
            for sub in STRICT_RISKS_FIELD_ORDER:
                if sub not in original_risks:
                    repairs.append(f"risks.{sub} (absent in original)")
                elif not isinstance(original_risks[sub], list):
                    repairs.append(
                        f"risks.{sub} (was {type(original_risks[sub]).__name__}, expected list)"
                    )
        return repairs

    def _find_order_repairs(
        self, strict_schema: Dict[str, Any], original_input: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Report fields whose original input order differed from canonical."""
        # Order only matters at strict_schema level (after Phase 1).
        # We compare actual key order in strict_schema vs canonical.
        canonical = STRICT_SCHEMA_FIELD_ORDER
        actual_keys = [k for k in strict_schema.keys() if k in canonical]
        canonical_present = [k for k in canonical if k in strict_schema]
        if actual_keys != canonical_present:
            return ["top-level field order differs from canonical"]
        # Check risks sub-order
        risks = strict_schema.get("risks") or {}
        if isinstance(risks, dict):
            actual_risk_keys = [k for k in risks.keys() if k in STRICT_RISKS_FIELD_ORDER]
            canonical_risk_present = [k for k in STRICT_RISKS_FIELD_ORDER if k in risks]
            if actual_risk_keys != canonical_risk_present:
                return ["risks sub-category order differs from canonical"]
        return []

    # ============================================================
    # Scoring
    # ============================================================

    def _consistency_score(self, strict_schema: Dict[str, Any]) -> float:
        """Field completeness 0-100. Counts non-empty fields vs 12 canonical.

        12 canonical = 7 top-level List fields + 5 nested risk categories.
        The `risks` field itself is not counted separately — its 5 sub-categories
        represent its "structure".
        """
        # 7 list top-level fields (excluding risks)
        non_empty_top = sum(
            1 for f in STRICT_SCHEMA_FIELD_ORDER
            if f != "risks" and strict_schema.get(f)
        )
        # 5 nested risk categories
        risks = strict_schema.get("risks") or {}
        non_empty_risk = sum(
            1 for s in STRICT_RISKS_FIELD_ORDER
            if isinstance(risks, dict) and risks.get(s)
        )
        non_empty = non_empty_top + non_empty_risk
        total_all = 7 + len(STRICT_RISKS_FIELD_ORDER)  # 12
        return round(non_empty / total_all * 100, 2)

    def _risk_score(self, strict_schema: Dict[str, Any]) -> float:
        """Risk structure completeness 0-100. All 5 categories populated = 100."""
        risks = strict_schema.get("risks") or {}
        if not isinstance(risks, dict):
            return 0.0
        populated = sum(
            1 for s in STRICT_RISKS_FIELD_ORDER
            if isinstance(risks.get(s), list) and len(risks[s]) > 0
        )
        return round(populated / len(STRICT_RISKS_FIELD_ORDER) * 100, 2)

    # ============================================================
    # Suggestions (structural prose only, R1)
    # ============================================================

    def _suggest(
        self,
        strict_schema: Dict[str, Any],
        missing: List[str],
        type_repairs: List[str],
        risk_repairs: List[str],
        consistency: float,
        risk: float,
    ) -> List[str]:
        """Generate structural suggestions (never code)."""
        suggestions: List[str] = []

        # Missing fields
        if missing:
            top_level_missing = [m for m in missing if "." not in m]
            if top_level_missing:
                suggestions.append(
                    f"GLM/DeepSeek prompts should explicitly request: {', '.join(top_level_missing)}"
                )
            risk_missing = [m for m in missing if m.startswith("risks.")]
            if risk_missing:
                suggestions.append(
                    f"DeepSeek should ensure risks contains all 5 categories: {', '.join(risk_missing)}"
                )

        # Type repairs
        if type_repairs:
            suggestions.append(
                "DeepSeek output is inconsistent in field types — see type_repairs for details"
            )
            suggestions.append(
                "Consider adding output schema examples to DeepSeek prompts to reduce type drift"
            )

        # Risk repairs
        if risk_repairs:
            suggestions.append(
                "Risks field structure is being normalized — DeepSeek prompt should require 5-category dict"
            )

        # Score-based suggestions
        if consistency < 50.0:
            suggestions.append(
                f"Consistency score {consistency} is low — review upstream prompt templates"
            )
        if risk < 50.0 and "risks" in strict_schema:
            suggestions.append(
                f"Risk score {risk} is low — most risk categories are empty"
            )
        if consistency == 100.0 and risk == 100.0:
            suggestions.append(
                "All canonical fields populated — strict schema is complete"
            )

        # Downstream hints (R5: structural only, no code)
        if type_repairs:
            suggestions.append(
                "豆包: expect to encounter type-coerced fields; ensure formatters handle list-of-strings"
            )
        if risk_repairs:
            suggestions.append(
                "Kimi: when interpreting risks, note that original may have been a list (Phase 1 normalized)"
            )

        return suggestions