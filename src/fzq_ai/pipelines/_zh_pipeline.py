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
from string import Template
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

        # V24-R2: civilization handle — bound BEFORE any stage try-block so a
        # failing GLM import can never leave `civ` unbound (the NameError at the
        # Doubao/Kimi stages below was being swallowed by their except clauses,
        # silently disabling both stages).
        civ = kwargs.get("civilization")

        # V24-R2: when civ is provided, run() (the main entry) also records the
        # pipeline input and attaches civilization_trace to the result — the
        # same contract run_async() already honors (BasePipeline does likewise).
        civ_trace: list[str] = []
        if civ and hasattr(civ, "remember"):
            try:
                safe_kwargs = {k: v for k, v in kwargs.items() if k != "civilization"}
                civ.remember(f"pipeline.{self.task_type}.input", repr(safe_kwargs)[:200])
                civ_trace.append(f"civilization.remember.pipeline.{self.task_type}")
            except Exception:
                _logger.warning("Suppressed error", exc_info=True)

        # 0. GLM extraction (content extraction before LLM structuring)
        glm_material = None
        try:
            from fzq_ai.glm.extractor import GLMExtractor
            extractor = GLMExtractor()
            glm_material = extractor.extract(user_input)
            if civ and hasattr(civ, "remember"):
                civ.remember("glm_raw", glm_material.model_dump())
                civ.remember("glm_quotes", [q.text for q in glm_material.raw_quotes])
                civ.remember("glm_events", [e.summary for e in glm_material.event_chain])
        except Exception:
            _logger.warning("GLM extraction skipped", exc_info=True)

        # 1. Load prompt
        try:
            prompt_template = self._load_prompt()
        except Exception as e:
            return self._fail(str(e), trace_id, t0, user_input, warning=f"prompt_load_failed: {e}")

        # 2. Fill prompt — string.Template + safe_substitute (P0-C11): the zh
        #    templates contain literal JSON braces, so str.format() always raised
        #    KeyError and silently fell back to the static instructions — the user
        #    input never reached the LLM. `$content` does not conflict with JSON
        #    braces, and each template ends with a 【待分析输入】 block holding it.
        try:
            prompt = Template(prompt_template).safe_substitute(
                content=user_input, intent=user_input, context=user_input,
            )
        except Exception:
            # Defensive fallback: use the raw template if substitution itself fails
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
        # V25: Minimax strict schema validation (single execution point — P0-C12;
        # run_async() no longer re-runs this pass)
        result["minimax"] = self._minimax_pass(result, civ=civ)

        # V25: Doubao formatting (Minimax → clean JSON for Kimi/Qwen)
        try:
            from fzq_ai.doubao.formatter import DoubaoFormatter
            from fzq_ai.pipeline.feedback_loop import FeedbackLoop
            fb_doubao = FeedbackLoop.build_context(civ=civ, target="doubao")
            fmt = DoubaoFormatter()
            result["doubao_formatted"] = fmt.format(
                result.get("validated") or result.get("parsed") or {},
                feedback_context=fb_doubao,
            )
            if civ and hasattr(civ, "remember"):
                civ.remember("doubao_formatted", str(result["doubao_formatted"])[:1000])
        except Exception:
            _logger.warning("Doubao formatting skipped", exc_info=True)

        # V25: Kimi interpretation (structured → human-readable explanations)
        try:
            from fzq_ai.interpreter.kimi_interpreter import KimiInterpreter
            from fzq_ai.pipeline.feedback_loop import FeedbackLoop
            fb_kimi = FeedbackLoop.build_context(civ=civ, target="kimi")
            interpreter = KimiInterpreter()
            doubao = result.get("doubao_formatted") or {}
            result["kimi_interpreted"] = interpreter.interpret(
                doubao,
                feedback_context=fb_kimi,
            ).model_dump()
            if civ and hasattr(civ, "remember"):
                civ.remember("kimi_interpreted", str(result["kimi_interpreted"].get("policy_brief", ""))[:1000])
        except Exception:
            _logger.warning("Kimi interpretation skipped", exc_info=True)

        # V24-R2: attach the civ trace when running under a civilization handle
        if civ is not None:
            result["civilization_trace"] = civ_trace

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

        # Forward civilization into run() so the GLM/Doubao/Kimi stages and the
        # single Minimax pass can use it (P0-C12: the duplicate _minimax_pass
        # that used to live here was removed — run() is the one execution point).
        result = await self.run(civilization=civilization, **kwargs)

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

        # 3. V25: Minimax Phase 2 — Structural Feedback Layer
        #    Generates structural feedback (no code, no schema changes) for
        #    upstream (GLM, DeepSeek) and downstream (豆包, Kimi, Qwen).
        #    Routed feedback is also written to civilization memory.
        #    (Minimax Phase 1 runs exactly once, inside run() — P0-C12 dedup.)
        self._minimax_phase2_pass(result, civ=civilization)

        # 4. V24.3.5: MinimaxFeedbackLoop — close the structural loop
        #    Persists Phase 2 routed feedback into civ with target-prefixed keys
        #    so downstream modules (GLM/Doubao/Kimi/Qwen) can OPTIONALLY read on
        #    next call. This is the wiring that turns Phase 2 reports into a
        #    self-correcting feedback cycle.
        self._minimax_feedback_loop_pass(result, civ=civilization)
        return result

    # ============================================================
    # V25: Minimax strict schema validation pass
    # ============================================================
    def _minimax_pass(self, result: Dict[str, Any], civ: Any = None) -> Dict[str, Any]:
        """Validate the pipeline's PARSED payload through Minimax (StrictSchemaValidator).

        P0-C12: the validation target is `result["parsed"]` — the actual LLM
        analysis payload. Previously the whole pipeline wrapper dict was fed to
        StrictSchema, which repair-stepped it into an all-empty schema yet still
        reported valid=True (false positive: "validation passed" while every
        real field had been discarded).

        If `parsed` is not a dict (e.g. JSON parse failed or the LLM call
        errored), validation is SKIPPED and a warning is recorded in both the
        log and `result["warnings"]` — no fabricated validation result.

        Minimax guarantees (on the parsed payload):
          - R1: Never fabricates facts (preserves all input keys with non-None values)
          - R2: Never infers content (no semantic expansion)
          - R3: Fills missing fields with empty defaults
          - R4: Repairs types (str -> list, dict -> list, etc.)
          - R5: Maintains canonical field order
          - R6: Output is always a Pydantic model (no natural language)

        Returns a sub-dict: {valid: bool, strict: dict | None, errors: list[str]}
        Pipeline never fails on Minimax errors — they're captured in the sub-dict.
        """
        parsed = result.get("parsed") if isinstance(result, dict) else None
        if not isinstance(parsed, dict):
            _logger.warning(
                "minimax validation skipped: result['parsed'] is %s, not a dict",
                type(parsed).__name__,
            )
            warnings_list = result.get("warnings") if isinstance(result, dict) else None
            if isinstance(warnings_list, list):
                warnings_list.append("minimax_validation_skipped: parsed_not_dict")
            return {
                "valid": False,
                "strict": None,
                "errors": [],
                "skipped": True,
            }
        try:
            from fzq_ai.minimax import StrictSchemaValidator
            validator = StrictSchemaValidator()
            strict = validator.validate_with_civ(parsed, civ=civ)
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

    # ============================================================
    # V25: Minimax Phase 2 — Structural Feedback Layer
    # ============================================================
    def _minimax_phase2_pass(self, result: Dict[str, Any], civ: Any = None) -> None:
        """Generate and route Phase 2 structural feedback.

        Phase 2 produces read-only structural feedback (no code, no schema changes).
        Result dict gets two new keys:
          - minimax_feedback: StructuralFeedback.model_dump()
          - minimax_feedback_routed: dict[str, RoutedFeedback] (6-target routing)

        If civ provided: writes 3 memory keys (consistency_score, risk_score,
        feedback trace_id) — best-effort, never blocks pipeline.
        """
        try:
            from fzq_ai.minimax.phase2 import (
                MinimaxFeedbackEngine,
                MinimaxFeedbackRouter,
            )
            minimax = result.get("minimax") or {}
            strict_schema = minimax.get("strict") if isinstance(minimax, dict) else None
            if not strict_schema:
                # Phase 1 failed or strict is None — skip Phase 2
                return

            engine = MinimaxFeedbackEngine()
            router = MinimaxFeedbackRouter()
            feedback = engine.generate(
                strict_schema=strict_schema,
                original_input=result,
                trace_id=result.get("trace_id"),
            )
            routed = router.route(feedback)

            result["minimax_feedback"] = feedback.model_dump()
            result["minimax_feedback_routed"] = routed

            # Civ memory (best-effort)
            if civ is not None and hasattr(civ, "remember"):
                try:
                    civ.remember("minimax_feedback_consistency", str(feedback.consistency_score))
                    civ.remember("minimax_feedback_risk", str(feedback.risk_score))
                    civ.remember("minimax_feedback_trace_id", feedback.trace_id)
                    civ.remember("minimax_feedback_missing_count", str(len(feedback.missing_fields)))
                    civ.remember("minimax_feedback_type_repair_count", str(len(feedback.type_repairs)))
                    civ.remember("minimax_feedback_risk_repair_count", str(len(feedback.risk_repairs)))
                except Exception:
                    pass
        except Exception as e:
            # Phase 2 must never break the pipeline
            _logger.warning("minimax phase 2 failed: %s", e, exc_info=True)
            result["minimax_feedback"] = {"error": f"{type(e).__name__}: {e}"}

    # ============================================================
    # V24.3.5: Minimax Feedback Loop — close the structural loop
    # ============================================================
    def _minimax_feedback_loop_pass(
        self, result: Dict[str, Any], civ: Any = None
    ) -> None:
        """Persist Phase 2 routed feedback to civ (target-prefixed keys).

        This is the wiring that closes the loop: Phase 2 generates feedback,
        the loop writes it into civ with `feedback.<target>.*` keys, and
        next-time GLM/Doubao/Kimi/Qwen calls can OPTIONALLY read it.

        Storage keys written (per V24.3.5 design):
          feedback._global.consistency_score / risk_score / trace_id /
              generated_at / missing_fields / type_repairs / risk_repairs /
              last_loop_write_at
          feedback.<target>.issues / issue_count / suggestions /
              priority / requires_action   (for glm/deepseek/doubao/kimi/qwen)
          feedback.ds.ds_tasks / requires_execution_book

        No-op if civ is None or MinimaxFeedbackLoop not importable.
        Never raises (best-effort, must not break pipeline).
        """
        try:
            from fzq_ai.minimax.phase2 import MinimaxFeedbackLoop

            routed = result.get("minimax_feedback_routed") or {}
            phase2_feedback_dict = result.get("minimax_feedback") or {}

            # Reconstruct StructuralFeedback if available (best-effort)
            phase2_feedback = None
            if isinstance(phase2_feedback_dict, dict) and phase2_feedback_dict.get("trace_id"):
                try:
                    from fzq_ai.minimax.phase2 import StructuralFeedback
                    phase2_feedback = StructuralFeedback(**phase2_feedback_dict)
                except Exception:
                    pass

            loop = MinimaxFeedbackLoop()
            ok = loop.record(
                routed_feedback=routed,
                civ=civ,
                phase2_feedback=phase2_feedback,
            )
            result["minimax_feedback_loop_ok"] = ok
        except Exception as e:
            _logger.warning("minimax feedback loop pass failed: %s", e, exc_info=True)
            result["minimax_feedback_loop_ok"] = False

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
