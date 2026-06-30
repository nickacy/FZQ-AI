# src/fzq_ai/agents/base.py
# V21 — Unified Agent Base Class
# 双语版（中文 + English）
# Author: Nick
# Version: V21.0.0

from __future__ import annotations
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

# ============================================================
# AgentContext — 智能体输入上下文
# ============================================================

@dataclass
class AgentContext:
    user_id: Optional[str]
    locale: str              # 如 "zh-CN"
    focus_regions: list[str] # 如 ["Global South", "Middle East"]
    languages: list[str]     # 如 ["zh", "en", "ar", "es"]
    raw_input: Any           # 原始新闻/链接/文本
    metadata: Dict[str, Any] # 任务元信息（来源、时间等）


# ============================================================
# AgentResult — 智能体输出结果
# ============================================================

@dataclass
class AgentResult:
    ok: bool
    data: Any
    warnings: list[str]
    trace: list[str]         # 执行链路记录（便于调试与评估）


# ============================================================
# BaseAgent — 智能体基础类（统一版）
# ============================================================

class BaseAgent(ABC):
    """
    ============================================================
    V21 — BaseAgent（统一智能体基类）
    ============================================================

    本类整合了：
    - 原 base.py 的 run(ctx)
    - 原 base_agent.py 的 plan/route/execute/evaluate/reflect/heal 等能力

    这是 FZQ‑AI 智能体层的唯一基类。
    所有智能体必须继承此类。

    ============================================================
    English Description
    ============================================================

    Unified BaseAgent class for the FZQ‑AI Agent Layer.
    Combines runtime interface + capability abstraction.
    """

    name: str

    def __init__(self, name: str):
        self.name = name
        self.memory: Dict[str, Any] = {}
        self.last_result: Optional[AgentResult] = None

    # ============================================================
    # 统一入口：run(ctx)
    # ============================================================

    def run(self, ctx: AgentContext) -> AgentResult:
        trace = []

        trace.append("Step 1: Planning")
        plan = self.plan(ctx)

        trace.append("Step 2: Model Routing")
        model = self.auto_select_model(plan)

        trace.append(f"Step 3: Executing with model: {model}")
        raw_result = self.execute(model, plan)

        trace.append("Step 4: Evaluating result")
        score = self.evaluate(raw_result)

        trace.append(f"Score = {score}")

        if score < 0.6:
            trace.append("Score too low → Reflection")
            raw_result = self.reflect(raw_result)

        if score < 0.5:
            trace.append("Score too low → Healing")
            raw_result = self.heal(raw_result)

        if score < 0.4:
            trace.append("Score too low → Retry")
            raw_result = self.retry(plan)

        result = AgentResult(
            ok=True,
            data=raw_result,
            warnings=[],
            trace=trace
        )

        self.last_result = result
        return result

    # ============================================================
    # 1. 任务规划 / Task Planning
    # ============================================================

    @abstractmethod
    def plan(self, ctx: AgentContext) -> Dict[str, Any]:
        pass

    # ============================================================
    # 2. 模型选择 / Model Routing
    # ============================================================

    @abstractmethod
    def route(self, plan: Dict[str, Any]) -> str:
        pass

    # ============================================================
    # 3. 执行任务 / Execution
    # ============================================================

    @abstractmethod
    def execute(self, model: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # ============================================================
    # 4. 质量评估 / Evaluation
    # ============================================================

    @abstractmethod
    def evaluate(self, result: Dict[str, Any]) -> float:
        pass

    # ============================================================
    # 5. 自我反思 / Reflection
    # ============================================================

    @abstractmethod
    def reflect(self, result: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # ============================================================
    # 6. 自愈系统 / Self‑Healing
    # ============================================================

    @abstractmethod
    def heal(self, result: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # ============================================================
    # 7. 记忆系统 / Memory Engine
    # ============================================================

    def memory_read(self, key: str) -> Any:
        return self.memory.get(key)

    def memory_write(self, key: str, value: Any) -> None:
        self.memory[key] = value

    # ============================================================
    # 8. 自动 fallback / retry
    # ============================================================

    @abstractmethod
    def fallback(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def retry(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        pass

    # ============================================================
    # 9. 自动模型选择 / Auto Model Selection
    # ============================================================

    @abstractmethod
    def auto_select_model(self, plan: Dict[str, Any]) -> str:
        pass
