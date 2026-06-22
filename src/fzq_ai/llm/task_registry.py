# fzq_ai/llm/task_registry.py
# FZQ‑AI v10 TaskRegistry（终极版）

from typing import Dict, List, Optional
from pydantic import BaseModel
from fzq_ai.config import settings


class TaskConfig(BaseModel):
    name: str
    description: str
    primary_model: str
    fallback_models: List[str]


class TaskRegistry:
    _instance: Optional["TaskRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks: Dict[str, TaskConfig] = {}
            cls._instance._register_tasks()
        return cls._instance

    def _register_tasks(self):
        task_definitions = [
            ("news_intel", "Analyze and summarize news items"),

            ("narrative_summary", "Generate narrative summary"),
            ("narrative_keypoints", "Extract key narrative points"),
            ("narrative_storyline", "Generate storyline"),
            ("narrative_implications", "Analyze narrative implications"),

            ("risk_summary", "Summarize risk factors"),
            ("risk_factors", "Extract structured risk factors"),
            ("risk_forecast", "Forecast risk trends"),

            ("sentiment_score", "Generate sentiment score"),
            ("sentiment_summary", "Summarize sentiment"),

            ("scenario_base_case", "Generate base case scenario"),
            ("scenario_alternatives", "Generate alternative scenarios"),
            ("scenario_drivers", "Identify key scenario drivers"),
            ("scenario_implications", "Scenario implications"),

            ("daily_exec_overview", "Executive overview section"),
            ("daily_top_stories", "Top stories section"),
            ("daily_risk_alerts", "Risk alerts section"),
            ("daily_outlook", "30–90 day outlook"),
        ]

        for name, desc in task_definitions:
            primary, fallback = settings.get_model_for_task(name)

            self._tasks[name] = TaskConfig(
                name=name,
                description=desc,
                primary_model=primary,
                fallback_models=fallback,
            )

    def get(self, name: str) -> TaskConfig:
        if name not in self._tasks:
            raise KeyError(f"Task '{name}' not registered")
        return self._tasks[name]

    def list_tasks(self) -> List[str]:
        return list(self._tasks.keys())

    def all(self) -> Dict[str, TaskConfig]:
        return self._tasks
