# fzq_ai/llm/task_registry.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TaskConfig:
    name: str
    default_provider: str
    fallback_chain: List[str]
    json_mode: bool = False
    require_reasoning: bool = False
    require_long_context: bool = False


class TaskRegistry:
    """
    任务注册表（统一管理所有 LLM 任务）
    """

    def __init__(self):
        self.tasks = {}

        # 注册所有任务
        self.register(
            TaskConfig(
                name="news_intel",
                default_provider="openai",
                fallback_chain=["openai", "deepseek", "minimax"],
                json_mode=True,
            )
        )

        self.register(
            TaskConfig(
                name="event_extraction",
                default_provider="openai",
                fallback_chain=["openai", "deepseek", "minimax"],
                json_mode=True,
            )
        )

        self.register(
            TaskConfig(
                name="risk_intel",
                default_provider="deepseek",
                fallback_chain=["deepseek", "openai", "minimax"],
                json_mode=False,
                require_reasoning=True,
            )
        )

        self.register(
            TaskConfig(
                name="sentiment",
                default_provider="openai",
                fallback_chain=["openai", "deepseek", "minimax"],
                json_mode=False,
            )
        )

    def register(self, config: TaskConfig):
        self.tasks[config.name] = config

    def get(self, task: str) -> TaskConfig:
        return self.tasks.get(task, self.tasks["sentiment"])
