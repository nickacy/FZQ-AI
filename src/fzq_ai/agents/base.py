# src/fzq_ai/agents/base.py
# V24 — Unified Agent Base Class
# 双语版（中文 + English）
# Author: Nick
# Version: V24.0.0

from __future__ import annotations
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

# ============================================================
# AgentContext — 智能体输入上下文
# ============================================================

class AgentContext(BaseModel):
    user_id: Optional[str] = None
    locale: str = "zh-CN"
    focus_regions: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    raw_input: Any = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    civilization: Optional[Any] = None  # V24-R2: civilization layer handle (set by EntryService)


# ============================================================
# AgentResult — 智能体输出结果
# ============================================================

class AgentResult(BaseModel):
    ok: bool = True
    data: Any = None
    warnings: list[str] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)


# ============================================================
# BaseAgent — 智能体基础类（统一版）
# ============================================================

class BaseAgent:
    """
    ============================================================
    V24 — BaseAgent（统一智能体基类）
    ============================================================

    设计要点：
    - 不强制实现：9 个钩子（plan / route / execute / evaluate / reflect /
      heal / fallback / retry / auto_select_model）均有合理默认实现，
      子类按需重写即可，不再被 ABC abstractmethod 阻止实例化
    - 提供默认 `run()`：plan → execute → reflect → heal
    - 子类可重写 `run()` 完全替换默认流程（如 zh_tasks/*_agent.py）
    - 兼容 V21 / V22 / V23 / V24 所有 agent 实现

    History note:
    - V21 起以 `class BaseAgent(ABC)` + 9 个 @abstractmethod 形式存在
    - 实际上绝大多数子类只重写 `run()`，9 个 abstractmethod 长期未实现
    - V24 移除 ABC + abstractmethod，既保留文档作用又允许子类灵活扩展
    """

    name: str

    def __init__(self, name: str):
        self.name = name
        self.memory: Dict[str, Any] = {}
        self.last_result: Optional[AgentResult] = None

    # ============================================================
    # 统一入口：run(ctx)  —  默认 plan → execute → reflect → heal
    # 子类可重写此方法完全替换默认流程（如 zh_tasks/*_agent.py）
    # ============================================================

    async def run(self, ctx: AgentContext) -> AgentResult:
        trace: List[str] = []

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
            trace=trace,
        )

        self.last_result = result
        return result

    # ============================================================
    # 可选钩子 — 子类按需重写（默认是 pass-through / 合理兜底）
    # ============================================================

    def plan(self, ctx: AgentContext) -> Dict[str, Any]:
        """Default: return ctx as plan. Subclasses can override."""
        return {"raw_input": ctx.raw_input, "metadata": ctx.metadata}

    def route(self, plan: Dict[str, Any]) -> str:
        """Default: no routing. Subclasses can override."""
        return ""

    def execute(self, model: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Default: empty execution. Subclasses can override."""
        return {}

    def evaluate(self, result: Dict[str, Any]) -> float:
        """Default: accept everything. Subclasses can override."""
        return 1.0

    def reflect(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Default: pass through. Subclasses can override."""
        return result

    def heal(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Default: pass through. Subclasses can override."""
        return result

    def fallback(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Default: empty fallback. Subclasses can override."""
        return {}

    def retry(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Default: empty retry. Subclasses can override."""
        return {}

    def auto_select_model(self, plan: Dict[str, Any]) -> str:
        """Default: empty model. Subclasses can override."""
        return ""

    # ============================================================
    # 记忆系统 / Memory Engine (V21 保留)
    # ============================================================

    def memory_read(self, key: str) -> Any:
        return self.memory.get(key)

    def memory_write(self, key: str, value: Any) -> None:
        self.memory[key] = value
