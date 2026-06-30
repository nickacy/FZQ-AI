# src/fzq_ai/agents/memory.py
# V21 — Memory Engine（记忆系统）
# 修复版：修复 Optional 未导入、类型注解不完整问题
# Author: Nick
# Version: V21.0.1

from __future__ import annotations
from typing import Any, Dict, List, Optional
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
    V21 — MemoryEngine（记忆系统）
    修复内容：
    - 添加 Optional 导入
    - 添加 __future__ annotations 解决类型解析问题
    - 统一类型注解
    """

    def __init__(self):
        # 短期记忆（只在当前任务中使用）
        self.session_memory: Dict[str, MemoryItem] = {}

        # 长期记忆（跨任务）
        self.long_term_memory: Dict[str, MemoryItem] = {}

        # 工作记忆（当前任务的中间状态）
        self.working_memory: Dict[str, Any] = {}

    # 写入短期记忆
    def write_session(self, key: str, value: Any, tags: Optional[List[str]] = None):
        self.session_memory[key] = MemoryItem(
            key=key,
            value=value,
            timestamp=time.time(),
            tags=tags or []
        )

    # 读取短期记忆
    def read_session(self, key: str) -> Optional[Any]:
        item = self.session_memory.get(key)
        return item.value if item else None

    # 写入长期记忆
    def write_long_term(self, key: str, value: Any, tags: Optional[List[str]] = None):
        self.long_term_memory[key] = MemoryItem(
            key=key,
            value=value,
            timestamp=time.time(),
            tags=tags or []
        )

    # 读取长期记忆
    def read_long_term(self, key: str) -> Optional[Any]:
        item = self.long_term_memory.get(key)
        return item.value if item else None

    # 标签检索（语义记忆）
    def search_by_tag(self, tag: str) -> List[Any]:
        results = []
        for item in self.long_term_memory.values():
            if tag in item.tags:
                results.append(item.value)
        return results

    # 工作记忆
    def write_working(self, key: str, value: Any):
        self.working_memory[key] = value

    def read_working(self, key: str) -> Optional[Any]:
        return self.working_memory.get(key)

    # 清理短期记忆
    def clear_session(self):
        self.session_memory.clear()

    # 清理工作记忆
    def clear_working(self):
        self.working_memory.clear()
