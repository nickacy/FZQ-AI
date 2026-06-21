# src/fzq_ai/agents/base.py
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class AgentContext:
    user_id: Optional[str]
    locale: str              # 如 "zh-CN"
    focus_regions: list[str] # 如 ["Global South", "Middle East"]
    languages: list[str]     # 如 ["zh", "en", "ar", "es"]
    raw_input: Any           # 原始新闻/链接/文本
    metadata: Dict[str, Any] # 任务元信息（来源、时间等）

@dataclass
class AgentResult:
    ok: bool
    data: Any
    warnings: list[str]
    trace: list[str]         # 执行链路记录（便于调试与评估）

class BaseAgent:
    name: str

    def run(self, ctx: AgentContext) -> AgentResult:
        raise NotImplementedError
