# fzq_ai/llm/task_registry.py
# Phase 4‑4 最终版（与 LLMRouter 完全兼容）

from typing import Dict, List, Optional
from pydantic import BaseModel


class TaskConfig(BaseModel):
    """单个任务类型的能力声明"""
    name: str
    description: str
    primary_model: str
    fallback_models: List[str]
    provider_priority: List[str]


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
    # 注册所有任务类型（17 个）
    # ------------------------------------------------------------
    def _register_default_tasks(self):
        tasks = [
            # -------------------------
            # News Intelligence
            # -------------------------
            TaskConfig(
                name="news_summarize",
                description="Summarize raw news text into structured insights",
                primary_model="gemini-1.5-flash",
                fallback_models=["gpt-3.5-turbo", "claude-haiku"],
                provider_priority=["gemini", "openai", "anthropic"],
            ),

            # -------------------------
            # Narrative Intelligence
            # -------------------------
            TaskConfig(
                name="narrative_summary",
                description="Generate narrative summary from news content",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),
            TaskConfig(
                name="narrative_keypoints",
                description="Extract key narrative points",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),
            TaskConfig(
                name="narrative_storyline",
                description="Generate storyline from news summary",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),
            TaskConfig(
                name="narrative_implications",
                description="Analyze implications of narrative",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),

            # -------------------------
            # Risk Intelligence
            # -------------------------
            TaskConfig(
                name="risk_summary",
                description="Summarize risk factors",
                primary_model="deepseek-chat",
                fallback_models=["gpt-4o-mini"],
                provider_priority=["deepseek", "openai"],
            ),
            TaskConfig(
                name="risk_factors",
                description="Extract structured risk factors",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),
            TaskConfig(
                name="risk_forecast",
                description="Forecast risk trends",
                primary_model="deepseek-chat",
                fallback_models=["gpt-4o-mini"],
                provider_priority=["deepseek", "openai"],
            ),

            # -------------------------
            # Sentiment Intelligence
            # -------------------------
            TaskConfig(
                name="sentiment_score",
                description="Generate sentiment score",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),
            TaskConfig(
                name="sentiment_summary",
                description="Summarize sentiment analysis",
                primary_model="gpt-4o-mini",
                fallback_models=["deepseek-chat"],
                provider_priority=["openai", "deepseek"],
            ),

            # -------------------------
            # Scenario Intelligence
            # -------------------------
            TaskConfig(
                name="scenario",
                description="Generate scenario analysis",
                primary_model="deepseek-chat",
                fallback_models=["gpt-4o-mini"],
                provider_priority=["deepseek", "openai"],
            ),

            # -------------------------
            # General Intelligence Tasks
            # -------------------------
            TaskConfig(
                name="multilingual_summary",
                description="Summarize content in multiple languages",
                primary_model="gemini-1.5-pro",
                fallback_models=["gpt-4o-mini"],
                provider_priority=["gemini", "openai"],
            ),
            TaskConfig(
                name="deep_reasoning",
                description="Deep reasoning and chain-of-thought tasks",
                primary_model="deepseek-chat",
                fallback_models=["gpt-4o"],
                provider_priority=["deepseek", "openai"],
            ),
            TaskConfig(
                name="structured_extraction",
                description="Extract structured data from unstructured text",
                primary_model="gpt-4o-mini",
                fallback_models=["gemini-1.5-flash"],
                provider_priority=["openai", "gemini"],
            ),

            # -------------------------
            # Daily Report Generation
            # -------------------------
            TaskConfig(
                name="daily_report_generate",
                description="Generate final daily intelligence report",
                primary_model="gpt-4o",
                fallback_models=["gemini-1.5-pro"],
                provider_priority=["openai", "gemini"],
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
