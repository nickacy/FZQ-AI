# src/fzq_ai/utils/tracing.py
# V24-Final — Unified Tracing (built-in JSON + optional LangFuse)
"""
Full-execution tracing for FZQ-AI V24.

Always records traces via structured JSON logs.
Optionally enables LangFuse when LANG_FUSE_PUBLIC_KEY is set.

Usage:
    from fzq_ai.utils.tracing import Tracer

    tracer = Tracer(trace_id=..., pipeline="risk_scan", agent="deepseek", model="deepseek-chat")
    span = tracer.span("pipeline.step1", duration_ms=120, success=True)
    tracer.llm_call(model="deepseek-chat", prompt="...", completion="...")
    tracer.set_timeline([...])
    tracer.set_state_machine({"current": "FINALIZE"})
    tracer.finish()
"""
from __future__ import annotations
import os
import time
import uuid
import logging
from typing import Any, Dict, List, Optional

from fzq_ai.utils.logger import log_event

logger = logging.getLogger(__name__)

# ── Optional LangFuse ────────────────────────────────────────

_LANGFUSE_AVAILABLE = False
_LF: Any = None


def _try_import_langfuse() -> bool:
    global _LANGFUSE_AVAILABLE, _LF
    if not os.getenv("LANGFUSE_PUBLIC_KEY") and not os.getenv("LANG_FUSE_PUBLIC_KEY"):
        return False
    try:
        from langfuse import Langfuse as _Langfuse
        _LF = _Langfuse()
        _LANGFUSE_AVAILABLE = True
        return True
    except ImportError:
        return False


# ── In-memory trace storage (for test introspection) ─────────

_trace_store: Dict[str, Dict[str, Any]] = {}


# ── Tracer ────────────────────────────────────────────────────

class Tracer:
    """Records full execution traces.  Always logs JSON.  Optionally pushes to LangFuse."""

    def __init__(
        self,
        *,
        trace_id: Optional[str] = None,
        pipeline: str = "unknown",
        agent: str = "unknown",
        model: str = "unknown",
    ):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.pipeline = pipeline
        self.agent = agent
        self.model = model
        self.spans: List[Dict[str, Any]] = []
        self.llm_calls: List[Dict[str, Any]] = []
        self.timeline: List[Dict[str, Any]] = []
        self.state_machine: Dict[str, Any] = {"current": "INIT"}
        self._start = time.time()
        self._finished = False

        # LangFuse trace (lazy)
        self._lf_trace: Any = None
        self._lf_ok = _try_import_langfuse()
        if self._lf_ok and _LF:
            try:
                self._lf_trace = _LF.trace(
                    name="fzq_ai_execution",
                    id=self.trace_id,
                    metadata={"pipeline": pipeline, "agent": agent, "model": model},
                )
            except Exception:
                self._lf_ok = False

        # Always log JSON
        log_event("trace.start",
            trace_id=self.trace_id, pipeline=pipeline, agent=agent, model=model)
        _trace_store[self.trace_id] = self._snapshot()

    # ── Span ──────────────────────────────────────────────────

    def span(self, name: str, **meta: Any) -> Dict[str, Any]:
        s = {"name": name, "timestamp": time.time(), **meta}
        self.spans.append(s)
        log_event("trace.span", trace_id=self.trace_id, **s)

        if self._lf_ok and self._lf_trace:
            try:
                self._lf_trace.span(name=name, metadata=s)
            except Exception:
                pass
        _trace_store[self.trace_id] = self._snapshot()
        return s

    # ── LLM call ──────────────────────────────────────────────

    def llm_call(
        self, model: str, prompt: str = "", completion: str = "", **meta: Any
    ) -> None:
        entry = {"model": model, "prompt": prompt[:200], "completion": completion[:200], **meta}
        self.llm_calls.append(entry)
        log_event("trace.llm_call", trace_id=self.trace_id, **entry)

        if self._lf_ok and self._lf_trace:
            try:
                self._lf_trace.generation(
                    name="llm_call", model=model, input=prompt, output=completion)
            except Exception:
                pass

    # ── Setters ───────────────────────────────────────────────

    def set_timeline(self, timeline: List[Dict[str, Any]]) -> None:
        self.timeline = timeline

    def set_state_machine(self, sm: Dict[str, Any]) -> None:
        self.state_machine = sm

    # ── Finish ────────────────────────────────────────────────

    def finish(self, success: bool = True) -> Dict[str, Any]:
        if self._finished:
            return self._snapshot()
        self._finished = True
        duration = (time.time() - self._start) * 1000
        log_event("trace.finish",
            trace_id=self.trace_id, duration_ms=duration, success=success,
            span_count=len(self.spans), llm_calls=len(self.llm_calls),
            timeline=self.timeline, state_machine=self.state_machine)

        if self._lf_ok and self._lf_trace:
            try:
                self._lf_trace.update(metadata={
                    "timeline": self.timeline,
                    "state_machine": self.state_machine,
                    "spans": len(self.spans),
                    "llm_calls": len(self.llm_calls),
                    "duration_ms": duration,
                })
            except Exception:
                pass

        _trace_store[self.trace_id] = self._snapshot()
        return self._snapshot()

    def _snapshot(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "pipeline": self.pipeline,
            "agent": self.agent,
            "model": self.model,
            "spans": list(self.spans),
            "llm_calls": list(self.llm_calls),
            "timeline": list(self.timeline),
            "state_machine": dict(self.state_machine),
        }


# ── Get trace for introspection ──────────────────────────────

def get_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    return _trace_store.get(trace_id)


def list_traces() -> List[str]:
    return list(_trace_store.keys())
