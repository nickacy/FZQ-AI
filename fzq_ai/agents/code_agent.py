# fzq_ai/agents/code_agent.py

from typing import Optional
from fzq_ai.llm.llm_router import LLMRouter


class CodeAgent:
    """
    代码分析 / 重构 / 调试 Agent
    - 所有模型选择交给 LLMRouter
    - 不再依赖 Claude
    """

    def __init__(self, router: LLMRouter):
        self.router = router

    # -----------------------------
    # 代码解释
    # -----------------------------
    def explain(self, code: str) -> str:
        prompt = f"请解释以下代码的功能，并指出潜在问题：\n\n{code}"
        return self.router.ask(prompt, task="code_explain")

    # -----------------------------
    # 代码重构
    # -----------------------------
    def refactor(self, code: str, goal: Optional[str] = None) -> str:
        goal_text = f"目标：{goal}\n\n" if goal else ""
        prompt = f"{goal_text}请重构以下代码，使其更简洁、可维护：\n\n{code}"
        return self.router.ask(prompt, task="refactor_code")

    # -----------------------------
    # 代码调试
    # -----------------------------
    def debug(self, code: str) -> str:
        prompt = f"请找出以下代码的错误，并给出修复后的版本：\n\n{code}"
        return self.router.ask(prompt, task="debug_code")

    # -----------------------------
    # 架构建议
    # -----------------------------
    def architecture(self, description: str) -> str:
        prompt = f"请根据以下需求提供系统架构建议：\n\n{description}"
        return self.router.ask(prompt, task="arch_design")
