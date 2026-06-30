# src/fzq_ai/agents/coop/protocol.py
# V22 — Agent Messaging Protocol（多智能体协作协议）
# Author: Nick
# Version: V22.1.0

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time


@dataclass
class AgentMessage:
    """
    多智能体消息结构（Agent → Agent）
    """
    sender: str
    receiver: str
    intent: str
    content: Any
    timestamp: float = time.time()
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentEnvelope:
    """
    包裹消息，用于黑板系统和调度器
    """
    message: AgentMessage
    delivered: bool = False
    read: bool = False


class AgentChannel:
    """
    多智能体通信通道（点对点）
    """

    def __init__(self):
        self._queue: List[AgentEnvelope] = []

    def send(self, msg: AgentMessage):
        envelope = AgentEnvelope(message=msg)
        self._queue.append(envelope)

    def receive(self, agent_name: str) -> List[AgentMessage]:
        msgs = []
        for env in self._queue:
            if env.message.receiver == agent_name and not env.read:
                env.read = True
                msgs.append(env.message)
        return msgs


class AgentIntent:
    """
    多智能体意图（用于协作推理链）
    """

    ANALYZE = "analyze"
    SUMMARIZE = "summarize"
    MERGE = "merge"
    PLAN = "plan"
    EXECUTE = "execute"
    WATCH = "watch"
    REPORT = "report"
