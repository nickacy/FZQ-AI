# src/fzq_ai/agents/memory.py
# V21 — Memory Engine（记忆系统）
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
import time

@dataclass
class MemoryItem:
    key: str
    value: Any
    timestamp: float
    tags: List[str]


class MemoryEngine:
    """
    ============================================================
    V21 — MemoryEngine（记忆系统）
    ============================================================

    功能：
    - 短期记忆（Session Memory）
    - 长期记忆（Long-Term Memory）
    - 语义记忆（Semantic Memory）
    - 工作记忆（Working Memory）
    - 自动过期机制
    - 标签检索（tag-based retrieval）

    ============================================================
    English Description
    ============================================================

    MemoryEngine stores and retrieves short-term, long-term,
    semantic, and working memory for agents.
    """

    def __init__(self):
        # 短期记忆（只在当前任务中使用）
        self.session_memory: Dict[str, MemoryItem] = {}

        # 长期记忆（跨任务）
        self.long_term_memory: Dict[str, MemoryItem] = {}

        # 工作记忆（当前任务的中间状态）
        self.working_memory: Dict[str, Any] = {}

    # ------------------------------------------------------------
    # Step 1: 写入短期记忆
    # ------------------------------------------------------------
    def write_session(self, key: str, value: Any, tags: List[str] = None):
        self.session_memory[key] = MemoryItem(
            key=key,
            value=value,
            timestamp=time.time(),
            tags=tags or []
        )

    # ------------------------------------------------------------
    # Step 2: 读取短期记忆
    # ------------------------------------------------------------
    def read_session(self, key: str) -> Any:
        item = self.session_memory.get(key)
        return item.value if item else None

    # ------------------------------------------------------------
    # Step 3: 写入长期记忆
    # ------------------------------------------------------------
    def write_long_term(self, key: str, value: Any, tags: List[str] = None):
        self.long_term_memory[key] = MemoryItem(
            key=key,
            value=value,
            timestamp=time.time(),
            tags=tags or []
        )

    # ------------------------------------------------------------
    # Step 4: 读取长期记忆
    # ------------------------------------------------------------
    def read_long_term(self, key: str) -> Any:
        item = self.long_term_memory.get(key)
        return item.value if item else None

    # ------------------------------------------------------------
    # Step 5: 标签检索（语义记忆）
    # ------------------------------------------------------------
    def search_by_tag(self, tag: str) -> List[Any]:
        results = []
        for item in self.long_term_memory.values():
            if tag in item.tags:
                results.append(item.value)
        return results

    # ------------------------------------------------------------
    # Step 6: 工作记忆（Working Memory）
    # ------------------------------------------------------------
    def write_working(self, key: str, value: Any):
        self.working_memory[key] = value

    def read_working(self, key: str) -> Any:
        return self.working_memory.get(key)

    # ------------------------------------------------------------
    # Step 7: 清理短期记忆（任务结束）
    # ------------------------------------------------------------
    def clear_session(self):
        self.session_memory.clear()

    # ------------------------------------------------------------
    # Step 8: 清理工作记忆（任务结束）
    # ------------------------------------------------------------
    def clear_working(self):
        self.working_memory.clear()
