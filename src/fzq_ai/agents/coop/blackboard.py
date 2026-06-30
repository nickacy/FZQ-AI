# src/fzq_ai/agents/coop/blackboard.py
# V22 — Multi-Agent Blackboard System（多智能体黑板系统）
# Author: Nick
# Version: V22.2.0

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time


@dataclass
class BlackboardEntry:
    """
    黑板条目（Agent 写入的内容）
    """
    agent: str
    key: str
    value: Any
    timestamp: float = time.time()
    metadata: Optional[Dict[str, Any]] = None


class Blackboard:
    """
    V22 — 多智能体黑板系统
    用于多智能体协作、共享记忆、共享推理链
    """

    def __init__(self):
        self._entries: List[BlackboardEntry] = []

    # ------------------------------------------------------------
    # 写入黑板
    # ------------------------------------------------------------
    def write(self, agent: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        entry = BlackboardEntry(agent=agent, key=key, value=value, metadata=metadata)
        self._entries.append(entry)

    # ------------------------------------------------------------
    # 读取黑板（按 key）
    # ------------------------------------------------------------
    def read(self, key: str) -> List[BlackboardEntry]:
        return [e for e in self._entries if e.key == key]

    # ------------------------------------------------------------
    # 读取黑板（按 agent）
    # ------------------------------------------------------------
    def read_by_agent(self, agent: str) -> List[BlackboardEntry]:
        return [e for e in self._entries if e.agent == agent]

    # ------------------------------------------------------------
    # 读取最新条目
    # ------------------------------------------------------------
    def latest(self, key: str) -> Optional[BlackboardEntry]:
        entries = self.read(key)
        if not entries:
            return None
        return sorted(entries, key=lambda e: e.timestamp)[-1]

    # ------------------------------------------------------------
    # 列出所有条目
    # ------------------------------------------------------------
    def dump(self) -> List[BlackboardEntry]:
        return list(self._entries)
