"""V24 — Structured pipeline base for zh_tasks.

All 4 zh_tasks pipelines share the same lifecycle:
  1. Load full prompt from `prompts/zh/<task>.txt` (via prompt_loader)
  2. Pick a model via V24 LLM Router (task-aware, failover chain)
  3. Call LLM through the unified `call_llm()` (with 3-tier failover)
  4. Parse LLM text into JSON (tolerating ```json fences and trailing text)
  5. Validate against the task's Pydantic schema (when parseable)
  6. Return a structured dict `{task, input, output, parsed, validation, model, provider, tokens, warnings, trace_id, duration_ms}`

Subclasses just declare `task_type`, `prompt_path`, and (optionally) override
`_extract_user_input()` for prompt variable substitution.
"""
from __future__ import annotations
import logging
import json
import re
import time
import uuid
from typing import Any, Dict, Optional, Type

from fzq_ai.pipelines.base import BasePipeline
from fzq_ai.llm.router import choose_model, call_llm
from fzq_ai.llm.failover import get_failover_chain
from fzq_ai.schemas.zh_tasks import SCHEMA_BY_TASK
from fzq_ai.utils.prompt_loader import load_prompt_template
_logger = logging.getLogger("fzq_ai._zh_pipeline")


# JSON code-fence pattern: ```json ... ``` or ``` ... ```
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
# First { ... } or [ ... ] block
_JSON_BLOCK_RE = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)


class ZhStructuredPipeline(BasePipeline):
    """Base for the 4 zh_tasks pipelines — see module docstring for lifecycle."""

    # Subclasses MUST set these
    task_type: str = ""           # e.g. "zh_policy_brief"
    prompt_path: str = ""         # relative to fzq_ai.prompts package

    # Optional: system role to prefix the prompt with.
    system_message: str = "你是一名专业的中文情报分析师。请严格按输出格式返回 JSON。"

    def __init__(self) -> None:
        # Resolve schema at instance time (class attr may be overridden)
        schema_cls = SCHEMA_BY_TASK.get(self.task_type)
        self.output_schema: Optional[Type] = schema_cls

    # ============================================================
    # 1. Prompt loading
    # ============================================================
    def _load_prompt(self) -> str:
        return load_prompt_template(self.prompt_path)

    # ============================================================
    # 2. Input extraction — accept req / content / input / text / topic
    # ============================================================
    def _extract_user_input(self, **kwargs: Any) -> str:
        for key in ("event_topic", "content", "input", "text", "query", "req"):
            v = kwargs.get(key)
            if v is None:
                continue
            if isinstance(v, str):
                return v
            if isinstance(v, dict):
                return json.dumps(v, ensure_ascii=False, default=str)
        return ""

    # ============================================================
    # 3. JSON parsing — tolerate markdown fences and prose
    # ============================================================
    @staticmethod
    def _parse_json(text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        # 1. Try direct parse
        try:
            v = json.loads(text)
            if isinstance(v, dict):
                return v
        except Exception:
            _logger.warning("Suppressed error", exc_info=True)
        # 2. Try fenced code block (```json ... ```)
        m = _FENCE_RE.search(text)
        if m:
            try:
                v = json.loads(m.group(1))
                if isinstance(v, dict):
                    return v
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)
        # 3. Try the first { ... } or [ ... ] block
        m = _JSON_BLOCK_RE.search(text)
        if m:
            try:
                v = json.loads(m.group(1))
                if isinstance(v, dict):
                    return v
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)
        return None

    # ============================================================
    # 4. Schema validation
    # ============================================================
    def _validate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.output_schema is None:
            return None
        try:
            obj = self.output_schema.model_validate(data)
            return obj.model_dump()
        except Exception as e:
            return {"_error": f"{type(e).__name__}: {e}", "_data": data}

    # ============================================================
    # 5. Core run() — sync interface
    # ============================================================
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        t0 = time.perf_counter()
        trace_id = str(uuid.uuid4())
        user_input = self._extract_user_input(**kwargs)
        warnings: list[str] = []

        # 1. Load prompt
        try:
            prompt_template = self._load_prompt()
        except Exception as e:
            return self._fail(str(e), trace_id, t0, user_input, warning=f"prompt_load_failed: {e}")

        # 2. Fill prompt
        try:
            prompt = prompt_template.format(intent=user_input, context=user_input)
        except Exception:
            # If template has no placeholders, use as-is
            prompt = prompt_template

        # 3. Pick model (V24 router)
        try:
            model = choose_model(self.task_type, lang="zh", length=len(user_input))
        except Exception as e:
            return self._fail(str(e), trace_id, t0, user_input, warning=f"choose_model_failed: {e}")

        # 4. Call LLM
        try:
            llm_text = await call_llm(
                model=model,
                prompt=prompt,
                trace_id=trace_id,
                task_type=self.task_type,
            )
        except Exception as e:
            return self._fail(str(e), trace_id, t0, user_input, warning=f"llm_call_failed: {e}",
                              model=model)

        # 5. Parse JSON
        parsed = self._parse_json(llm_text)
        if parsed is None:
            warnings.append("json_parse_failed")

        # 6. Schema validate
        validated = None
        if parsed is not None:
            validated = self._validate(parsed)
            if validated is not None and "_error" in validated:
                warnings.append(f"schema_validation_failed: {validated['_error']}")
                validated = None

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        result = {
            "task": self.task_type,
            "input": user_input,
            "output": llm_text,           # raw LLM text (always)
            "parsed": parsed,             # dict or None
            "validated": validated,       # dict (validated via Pydantic) or None
            "model": model,
            "fallback_chain": get_failover_chain(model),
            "warnings": warnings,
            "trace_id": trace_id,
            "duration_ms": duration_ms,
            "status": "ok" if validated is not None else "partial",
        }
        # V25: Minimax strict schema validation (default-on, even on sync run() path)
        result["minimax"] = self._minimax_pass(result, civ=None)
        return result

    async def run_async(self, **kwargs: Any) -> Dict[str, Any]:
        # V24-R2: civilization integration (kwargs shape, see agent task wrappers)
        civilization = kwargs.pop("civilization", None)
        civ_trace: list[str] = []

        # 1. Pre-civ: remember pipeline task + input
        if civilization and hasattr(civilization, "remember"):
            try:
                civilization.remember(f"pipeline.{self.task_type}.input",
                                       repr(kwargs)[:200])
                civ_trace.append(f"civilization.remember.pipeline.{self.task_type}")
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        result = await self.run(**kwargs)

        # 2. Post-civ: snapshot + status remember
        if civilization and hasattr(civilization, "snapshot"):
            try:
                result["civilization_snapshot"] = civilization.snapshot()
                civ_trace.append(f"civilization.snapshot.pipeline.{self.task_type}")
            except Exception:
                result["civilization_snapshot"] = None

        if civilization and hasattr(civilization, "remember"):
            try:
                status = str(result.get("status", "ok"))
                civilization.remember(f"pipeline.{self.task_type}.status", status)
                civ_trace.append(f"civilization.remember.pipeline.{self.task_type}.status")
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        result["civilization_trace"] = civ_trace

        # 3. V25: Minimax strict schema validation (default-on)
        #    Validates the result dict's structure against StrictSchema (13 fields).
        #    Never modifies the input result (R1, R2, R5 compliance).
        #    On failure: sets minimax.valid=False with errors captured; pipeline still succeeds.
        result["minimax"] = self._minimax_pass(result, civ=civilization)
        return result

    # ============================================================
    # V25: Minimax strict schema validation pass
    # ============================================================
    def _minimax_pass(self, result: Dict[str, Any], civ: Any = None) -> Dict[str, Any]:
        """Validate pipeline result through Minimax (StrictSchemaValidator).

        Minimax guarantees:
          - R1: Never fabricates facts (preserves all input keys with non-None values)
          - R2: Never infers content (no semantic expansion)
          - R3: Fills missing fields with empty defaults
          - R4: Repairs types (str -> list, dict -> list, etc.)
          - R5: Maintains canonical field order
          - R6: Output is always a Pydantic model (no natural language)

        Returns a sub-dict: {valid: bool, strict: dict | None, errors: list[str]}
        Pipeline never fails on Minimax errors — they're captured in the sub-dict.
        """
        try:
            from fzq_ai.minimax import StrictSchemaValidator
            validator = StrictSchemaValidator()
            strict = validator.validate_with_civ(result, civ=civ)
            return {
                "valid": True,
                "strict": strict.model_dump(),
                "errors": [],
            }
        except Exception as e:
            _logger.warning("minimax validation failed: %s", e, exc_info=True)
            return {
                "valid": False,
                "strict": None,
                "errors": [f"{type(e).__name__}: {e}"],
            }

    def _fail(self, error: str, trace_id: str, t0: float, user_input: str,
              warning: str = "", model: str = "") -> Dict[str, Any]:
        result = {
            "task": self.task_type,
            "input": user_input,
            "output": "",
            "parsed": None,
            "validated": None,
            "model": model,
            "warnings": [warning] if warning else [error],
            "trace_id": trace_id,
            "duration_ms": round((time.perf_counter() - t0) * 1000, 2),
            "status": "error",
            "error": error,
            "civilization_trace": [],  # V24-R2: error path also carries empty trace
        }
        # V25: Minimax still runs on error path (validates structural completeness
        # of the error result itself — empty schema is also a valid StrictSchema).
        result["minimax"] = self._minimax_pass(result, civ=None)
        return result
