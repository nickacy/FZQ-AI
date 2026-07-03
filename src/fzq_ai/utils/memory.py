# src/fzq_ai/utils/memory.py
# V24-Final — Agent Memory Engine
"""
Layered memory system for FZQ-AI agents.

  Short-term (Working Memory): per-request, volatile
  Long-term (Persistent Memory): cross-request, survives session restart
  Episodic: execution timeline

Integrated with: Tracing, Monitoring, Structlog, Orchestrator.
"""
from __future__ import annotations
import json
import os
import threading
import time
from typing import Any, Dict, Optional

from fzq_ai.utils.logger import log_event

# ── Memory Engine ─────────────────────────────────────────────

class MemoryEngine:
    """Central memory store for all agents."""

    def __init__(self, persist_path: Optional[str] = None):
        self._lock = threading.Lock()
        self.short_term: Dict[str, Dict[str, Any]] = {}   # agent → {key: value}
        self.long_term: Dict[str, Dict[str, Any]] = {}    # agent → {key: value}
        self.episodic: list[Dict[str, Any]] = []          # timeline entries
        self._persist_path = persist_path
        self._hits: Dict[str, int] = {}
        self._misses: Dict[str, int] = {}
        if persist_path and os.path.exists(persist_path):
            self._load()

    # ── Short-term ──────────────────────────────────────────

    def remember(self, agent: str, key: str, value: Any) -> None:
        """Store in working memory."""
        with self._lock:
            self.short_term.setdefault(agent, {})[key] = value
            self._add_episode(agent, "remember", key, value)

    def recall(self, agent: str, key: str, default: Any = None) -> Any:
        """Retrieve from working memory."""
        with self._lock:
            entry = self.short_term.get(agent, {})
            if key in entry:
                self._hits[agent] = self._hits.get(agent, 0) + 1
                return entry[key]
            self._misses[agent] = self._misses.get(agent, 0) + 1
            return default

    def clear_short_term(self, agent: Optional[str] = None) -> None:
        """Clear working memory for one or all agents."""
        with self._lock:
            if agent:
                self.short_term.pop(agent, None)
            else:
                self.short_term.clear()

    # ── Long-term ────────────────────────────────────────────

    def store(self, agent: str, key: str, value: Any) -> None:
        """Store in persistent long-term memory."""
        with self._lock:
            self.long_term.setdefault(agent, {})[key] = value
            self._add_episode(agent, "store", key, value)
            self._persist()

    def retrieve(self, agent: str, key: str, default: Any = None) -> Any:
        """Retrieve from long-term memory."""
        with self._lock:
            return self.long_term.get(agent, {}).get(key, default)

    # ── Episodic ─────────────────────────────────────────────

    def _add_episode(self, agent: str, action: str, key: str, value: Any) -> None:
        self.episodic.append({
            "timestamp": time.time(),
            "agent": agent,
            "action": action,
            "key": key,
            "value_snippet": repr(value)[:200],
        })
        if len(self.episodic) > 1000:  # cap
            self.episodic = self.episodic[-500:]

    # ── Stats ────────────────────────────────────────────────

    def hit_rate(self, agent: str) -> float:
        h = self._hits.get(agent, 0)
        total = h + self._misses.get(agent, 0)
        return h / total if total else 0.0

    def snapshot(self, agent: str) -> Dict[str, Any]:
        """Full memory snapshot for execution.memory."""
        return {
            "short_term": dict(self.short_term.get(agent, {})),
            "long_term": dict(self.long_term.get(agent, {})),
            "episodic": [e for e in self.episodic if e["agent"] == agent][-20:],
            "hit_rate": round(self.hit_rate(agent), 3),
        }

    # ── Persistence ──────────────────────────────────────────

    def _persist(self) -> None:
        if not self._persist_path:
            return
        try:
            data = {"long_term": self.long_term, "hits": self._hits, "misses": self._misses}
            with open(self._persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, default=str)
        except Exception:
            pass

    def _load(self) -> None:
        try:
            with open(self._persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.long_term = data.get("long_term", {})
            self._hits = data.get("hits", {})
            self._misses = data.get("misses", {})
        except Exception:
            pass


# ── Global instance ──────────────────────────────────────────

global_memory = MemoryEngine()
