# fzq_ai/llm/task_registry.py
# FZQ‑AI v9.4 终极版 TaskRegistry（与 LLMRouter / Providers 完全对齐）

from typing import Dict, List, Optional
from pydantic import BaseModel


class TaskConfig(BaseModel):
    """单个任务类型的能力声明"""
    name: str
    description: str
    primary_model: str
    fallback_models: List[str]


class TaskRegistry:
    """全局任务注册中心（单例）"""

    _instance: Optional["TaskRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks: Dict[str, TaskConfig] = {}
            cls._instance._register_default_tasks()
        return cls._instance

    # ------------------------------------------------------------
    # 注册所有任务类型（与 pipelines 完全对齐）
    # ------------------------------------------------------------
    def _register_default_tasks(self):
        tasks = [

            # ======================================================
            # News Intelligence
            # ======================================================
            TaskConfig(
                name="news_intel",
                description="Analyze and summarize news items",
                primary_model="deepseek",
                fallback_models=["openai", "gemini"],
            ),

            # ======================================================
            # Narrative Intelligence
            # ======================================================
            TaskConfig(
                name="narrative_summary",
                description="Generate narrative summary",
                primary_model="openai",
                fallback_models=["deepseek", "gemini"],
            ),
            TaskConfig(
                name="narrative_keypoints",
                description="Extract key narrative points",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),
            TaskConfig(
                name="narrative_storyline",
                description="Generate storyline",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),
            TaskConfig(
                name="narrative_implications",
                description="Analyze narrative implications",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),

            # ======================================================
            # Risk Intelligence
            # ======================================================
            TaskConfig(
                name="risk_summary",
                description="Summarize risk factors",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),
            TaskConfig(
                name="risk_factors",
                description="Extract structured risk factors",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),
            TaskConfig(
                name="risk_forecast",
                description="Forecast risk trends",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),

            # ======================================================
            # Sentiment Intelligence
            # ======================================================
            TaskConfig(
                name="sentiment_score",
                description="Generate sentiment score",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),
            TaskConfig(
                name="sentiment_summary",
                description="Summarize sentiment",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),

            # ======================================================
            # Scenario Intelligence（4 个子任务）
            # ======================================================
            TaskConfig(
                name="scenario_base_case",
                description="Generate base case scenario",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),
            TaskConfig(
                name="scenario_alternatives",
                description="Generate alternative scenarios",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),
            TaskConfig(
                name="scenario_drivers",
                description="Identify key scenario drivers",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),
            TaskConfig(
                name="scenario_implications",
                description="Scenario implications",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),

            # ======================================================
            # Daily Report Intelligence（4 个子任务）
            # ======================================================
            TaskConfig(
                name="daily_exec_overview",
                description="Executive overview section",
                primary_model="openai",
                fallback_models=["gemini"],
            ),
            TaskConfig(
                name="daily_top_stories",
                description="Top stories section",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),
            TaskConfig(
                name="daily_risk_alerts",
                description="Risk alerts section",
                primary_model="deepseek",
                fallback_models=["openai"],
            ),
            TaskConfig(
                name="daily_outlook",
                description="30–90 day outlook",
                primary_model="openai",
                fallback_models=["deepseek"],
            ),
        ]

        for t in tasks:
            self._tasks[t.name] = t

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def get(self, name: str) -> TaskConfig:
        if name not in self._tasks:
            raise KeyError(f"Task '{name}' not registered")
        return self._tasks[name]

    def list_tasks(self) -> List[str]:
        return list(self._tasks.keys())

    def all(self) -> Dict[str, TaskConfig]:
        return self._tasks
